package com.neurologicaldisorder.DTO;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;

@Getter
@Builder
@AllArgsConstructor
public class RegisterResponse {

    private Integer userId;

    private String username;

    private String email;

    private String role;

    private String message;
}