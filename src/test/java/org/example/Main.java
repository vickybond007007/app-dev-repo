package org.example;// Online Java Compiler
// Use this editor to write, compile and run your Java code online
import java.util.*;

class Main {

    public static String reverseString(String str){

        StringBuilder sb = new StringBuilder();

       for(int i =0, j = str.length()-1; i < str.length() && j >=0 ; i++ , j--){
            
            if(!Character.isLetter(str.charAt(i))){
                sb.append(" ");
            }else{
                sb.append(str.charAt(j));
            }
        }
        System.out.print(sb.toString());

        return sb.toString();
    }



    public static void main(String[] args) {
        
        /*input: Mr Vikas Bhandari
        output: Ir Adnah Bsakivrm*/
        String str =  "Mr Vikas Bhandari";


        reverseString(str);



    }
}