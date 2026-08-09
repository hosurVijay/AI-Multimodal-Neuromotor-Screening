package com.neurologicaldisorder.Controller;

import com.neurologicaldisorder.Dto.ForgotPasswordRequest;
import com.neurologicaldisorder.Dto.LoginRequest;
import com.neurologicaldisorder.Dto.LoginResponse;
import com.neurologicaldisorder.DTO.RegisterRequest;
import com.neurologicaldisorder.DTO.RegisterResponse;
import com.neurologicaldisorder.Dto.ResetPasswordRequest;
import com.neurologicaldisorder.Service.AuthService;

import jakarta.validation.Valid;

import lombok.RequiredArgsConstructor;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;


    @PostMapping("/login")
    public ResponseEntity<LoginResponse> login(
            @Valid @RequestBody LoginRequest request) {

        return ResponseEntity.ok(
                authService.login(request)
        );
    }


    @PostMapping("/register")
    public ResponseEntity<RegisterResponse> register(
            @Valid @RequestBody RegisterRequest request) {

        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(authService.register(request));
    }

    @PostMapping("/forgot-password")
    public ResponseEntity<String> forgotPassword(
            @Valid @RequestBody ForgotPasswordRequest request) {

        authService.forgotPassword(
                request.getEmail()
        );

        return ResponseEntity.ok(
                "If the email is registered, "
                        + "a password reset link has been sent."
        );
    }
    @PostMapping("/reset-password")
    public ResponseEntity<String> resetPassword(
            @Valid @RequestBody ResetPasswordRequest request) {

        authService.resetPassword(
                request.getToken(),
                request.getNewPassword()
        );

        return ResponseEntity.ok(
                "Password reset successfully"
        );
    }
}