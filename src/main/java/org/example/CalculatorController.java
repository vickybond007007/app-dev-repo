package org.example;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/calculate")
public class CalculatorController {

    @GetMapping("/sum")
    public CalculationResponse sum(@RequestParam int a, @RequestParam int b) {
        return new CalculationResponse("sum", a, b, App.calculateSum(a, b));
    }

    @GetMapping("/diff")
    public CalculationResponse diff(@RequestParam int a, @RequestParam int b) {
        return new CalculationResponse("diff", a, b, App.calculateDiff(a, b));
    }

    @GetMapping({"/multiple", "/multiply"})
    public CalculationResponse multiple(@RequestParam int a, @RequestParam int b) {
        return new CalculationResponse("multiple", a, b, App.calculateMultiple(a, b));
    }
}
