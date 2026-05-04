package org.example;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class App {

    public int instancevar1;
    public String instancevar2;

    public App() {
    }

    public App(int instancevar1, String instancevar2){
        this.instancevar1 = instancevar1;
        this.instancevar2 = instancevar2;
    }

    public static int calculateSum(int a, int b){
        return a + b;
    }

    public static int calculateDiff(int a, int b){
        return a - b;
    }

    public static int calculateMultiple(int a, int b){
        return a * b;
    }

    public static int calculateDivide(int a, int b){
        return a / b;
    }

    public static void main(String[] args) {
        SpringApplication.run(App.class, args);
    }
}
