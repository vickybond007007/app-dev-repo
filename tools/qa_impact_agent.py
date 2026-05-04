#!/usr/bin/env python3
import argparse
import csv
import fnmatch
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree


def normalize_key(value):
    return re.sub(r"[^a-z0-9]", "", value.lower())


def load_changed_files(path):
    changed = []
    for raw_line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split()
        status = parts[0]
        file_path = parts[-1].replace("\\", "/")
        changed.append({"status": status, "path": file_path})
    return changed


def load_rules(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def path_matches(pattern, file_path):
    pattern = pattern.replace("\\", "/")
    file_path = file_path.replace("\\", "/")
    return fnmatch.fnmatch(file_path, pattern) or file_path == pattern


def find_test_sheet(qa_repo):
    candidates = []
    for extension in ("*.csv", "*.json", "*.xlsx"):
        candidates.extend(Path(qa_repo).rglob(extension))

    ranked = sorted(
        candidates,
        key=lambda p: (
            0 if re.search(r"test.?case|test.?sheet|regression", p.name, re.I) else 1,
            len(str(p)),
        ),
    )
    return ranked[0] if ranked else None


def load_csv_sheet(path):
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def load_json_sheet(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    for key in ("testCases", "test_cases", "tests"):
        if isinstance(data.get(key), list):
            return data[key]
    return []


def xlsx_cell_value(cell, shared_strings):
    value = cell.find("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v")
    if value is None:
        return ""
    text = value.text or ""
    if cell.attrib.get("t") == "s":
        try:
            return shared_strings[int(text)]
        except (ValueError, IndexError):
            return text
    return text


def load_xlsx_sheet(path):
    rows = []
    with zipfile.ZipFile(path) as workbook:
        shared_strings = []
        if "xl/sharedStrings.xml" in workbook.namelist():
            root = ElementTree.fromstring(workbook.read("xl/sharedStrings.xml"))
            for item in root.findall("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si"):
                texts = item.findall(".//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t")
                shared_strings.append("".join(text.text or "" for text in texts))

        sheet_name = "xl/worksheets/sheet1.xml"
        if sheet_name not in workbook.namelist():
            return []
        root = ElementTree.fromstring(workbook.read(sheet_name))
        for row in root.findall(".//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row"):
            values = [
                xlsx_cell_value(cell, shared_strings)
                for cell in row.findall("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c")
            ]
            rows.append(values)

    if not rows:
        return []
    headers = [str(header).strip() for header in rows[0]]
    records = []
    for values in rows[1:]:
        record = {}
        for index, header in enumerate(headers):
            record[header] = values[index] if index < len(values) else ""
        records.append(record)
    return records


def load_test_sheet(path):
    if not path:
        return []
    suffix = Path(path).suffix.lower()
    if suffix == ".csv":
        return load_csv_sheet(path)
    if suffix == ".json":
        return load_json_sheet(path)
    if suffix == ".xlsx":
        return load_xlsx_sheet(path)
    return []


def get_test_case_id(record):
    id_keys = {"testcaseid", "testcase", "tcid", "id", "testid"}
    for key, value in record.items():
        if normalize_key(str(key)) in id_keys:
            return str(value).strip()
    return ""


def select_test_records(records, selected_ids):
    selected = []
    selected_id_set = set(selected_ids)
    for record in records:
        test_id = get_test_case_id(record)
        if test_id in selected_id_set:
            selected.append(record)
    return selected


def analyze(changed_files, diff_text, rules_config, qa_repo):
    matched_rules = []
    selected_ids = []
    areas = []
    tags = list(rules_config.get("defaults", {}).get("regression_tags", []))
    new_test_ideas = []

    for rule in rules_config.get("rules", []):
        rule_patterns = rule.get("patterns", [])
        matches = [
            changed["path"]
            for changed in changed_files
            if any(path_matches(pattern, changed["path"]) for pattern in rule_patterns)
        ]
        if not matches:
            continue

        matched_rules.append({"name": rule.get("name", "Unnamed rule"), "matched_files": matches})
        selected_ids.extend(rule.get("test_case_ids", []))
        areas.extend(rule.get("areas", []))
        tags.extend(rule.get("regression_tags", []))
        new_test_ideas.extend(rule.get("new_test_case_ideas", []))

    if "@RequestParam" in diff_text:
        new_test_ideas.append("Verify required request parameters reject missing and invalid values.")
    if "@GetMapping" in diff_text:
        new_test_ideas.append("Verify changed GET endpoints are callable from browser and automation clients.")

    sheet_path = find_test_sheet(qa_repo) if qa_repo and Path(qa_repo).exists() else None
    sheet_records = load_test_sheet(sheet_path) if sheet_path else []

    selected_ids = sorted(set(selected_ids))
    selected_records = select_test_records(sheet_records, selected_ids)

    return {
        "summary": {
            "changed_file_count": len(changed_files),
            "matched_rule_count": len(matched_rules),
            "test_sheet_found": str(sheet_path) if sheet_path else None,
            "qa_repo_has_pom": bool(qa_repo and Path(qa_repo, "pom.xml").exists()),
        },
        "changed_files": changed_files,
        "changed_areas": sorted(set(areas)),
        "matched_rules": matched_rules,
        "recommended_regression_tags": sorted(set(tags)),
        "recommended_test_case_ids": selected_ids,
        "selected_test_cases_from_sheet": selected_records,
        "new_test_cases_needed": sorted(set(new_test_ideas)),
        "execution": {
            "recommended_command": rules_config.get("defaults", {}).get("test_command", "mvn clean test"),
            "note": "Use recommended_test_case_ids or selected_test_cases_from_sheet to wire selective execution once the QA repo supports tags, groups, or test IDs.",
        },
    }


def write_report(result, output_path):
    lines = [
        "# QA Impact Report",
        "",
        "## Changed Areas",
    ]
    lines.extend(f"- {area}" for area in result["changed_areas"] or ["No mapped area found"])
    lines.extend(["", "## Recommended Existing Test Cases"])
    lines.extend(f"- {test_id}" for test_id in result["recommended_test_case_ids"] or ["No mapped test case IDs found"])
    lines.extend(["", "## Recommended Regression Tags"])
    lines.extend(f"- {tag}" for tag in result["recommended_regression_tags"] or ["No tags selected"])
    lines.extend(["", "## New Test Cases To Consider"])
    lines.extend(f"- {idea}" for idea in result["new_test_cases_needed"] or ["No new test ideas generated"])
    lines.extend(["", "## Notes"])
    if result["summary"]["test_sheet_found"]:
        lines.append(f"- Test sheet found: `{result['summary']['test_sheet_found']}`")
    else:
        lines.append("- No QA test sheet found. Add CSV, JSON, or XLSX test case sheet to the QA repo.")
    if not result["summary"]["qa_repo_has_pom"]:
        lines.append("- QA repo does not currently contain `pom.xml`, so Jenkins will skip automation execution.")
    Path(output_path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Analyze dev changes and recommend QA regression scope.")
    parser.add_argument("--changed-files", required=True)
    parser.add_argument("--diff", required=True)
    parser.add_argument("--qa-repo", required=True)
    parser.add_argument("--rules", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-report", required=True)
    args = parser.parse_args()

    changed_files = load_changed_files(args.changed_files)
    diff_text = Path(args.diff).read_text(encoding="utf-8", errors="replace") if Path(args.diff).exists() else ""
    rules_config = load_rules(args.rules)
    result = analyze(changed_files, diff_text, rules_config, args.qa_repo)

    Path(args.output_json).write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_report(result, args.output_report)
    print(json.dumps(result["summary"], indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
