package com.neurologicaldisorder.Controller;

import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
public class UserController {


    @GetMapping("/protected")
    public String protectedEndpoint(Authentication authentication) {

        return "Authenticated successfully. Logged in as: "
                + authentication.getName();
    }

    @GetMapping("/doctor")
    public String doctorEndpoint(
            Authentication authentication) {

        return "Doctor endpoint. Logged in as: "
                + authentication.getName();
    }

    @GetMapping("/admin")
    public String adminEndpoint(
            Authentication authentication) {

        return "Admin endpoint. Logged in as: "
                + authentication.getName();
    }

}
