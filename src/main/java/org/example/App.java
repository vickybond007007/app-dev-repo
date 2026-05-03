package org.example;

/**
 * Hello world!
 */
public class App {

    public int instancevar1;
    public String instancevar2;
    
    public App(int instancevar1, String instancevar2){
        this.instancevar1 = instancevar1;
        this.instancevar2 = instancevar2;
    }

    public int calculateSum(int a, int b){
        return a + b;
    }
    
    public static void main(String[] args) {
        System.out.println("Hello World!");
        System.out.println("Hello World!--new chnages");
    }
}
