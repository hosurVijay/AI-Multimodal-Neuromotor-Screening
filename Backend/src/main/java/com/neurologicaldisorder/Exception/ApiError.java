package com.neurologicaldisorder.Exception;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
@Builder
@AllArgsConstructor
public class ApiError {

    private int status;

    private String message;

    private LocalDateTime timestamp;
}