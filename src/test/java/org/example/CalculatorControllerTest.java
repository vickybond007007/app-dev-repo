package org.example;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(CalculatorController.class)
class CalculatorControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void returnsSum() throws Exception {
        mockMvc.perform(get("/api/calculate/sum").param("a", "1").param("b", "3"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.operation").value("sum"))
                .andExpect(jsonPath("$.result").value(4));
    }

    @Test
    void returnsDiff() throws Exception {
        mockMvc.perform(get("/api/calculate/diff").param("a", "5").param("b", "3"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.operation").value("diff"))
                .andExpect(jsonPath("$.result").value(2));
    }

    @Test
    void returnsMultiple() throws Exception {
        mockMvc.perform(get("/api/calculate/multiple").param("a", "5").param("b", "3"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.operation").value("multiple"))
                .andExpect(jsonPath("$.result").value(15));
    }
}
