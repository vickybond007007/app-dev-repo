package org.example;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

public class AppTest {

    @Test
    public void calculatesSum() {
        assertEquals(4, App.calculateSum(1, 3));
    }

    @Test
    public void calculatesDiff() {
        assertEquals(2, App.calculateDiff(5, 3));
    }

    @Test
    public void calculatesMultiple() {
        assertEquals(15, App.calculateMultiple(5, 3));
    }
}
