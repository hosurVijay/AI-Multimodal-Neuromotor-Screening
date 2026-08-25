package com.neurologicaldisorder.Dto;

import com.neurologicaldisorder.Model.Gender;
import com.neurologicaldisorder.Model.PatientStatus;
import jakarta.validation.constraints.*;
import lombok.Getter;
import lombok.Setter;

import java.math.BigDecimal;
import java.time.LocalDate;

@Getter
@Setter
public class PatientRequest {

    @NotBlank(message = "Full name is required")
    private String fullName;

    private String profileImage;

    @NotNull(message = "Date of birth is required")
    @Past(message = "Date of birth must be in the past")
    private LocalDate dateOfBirth;

    @NotNull(message = "Gender is required")
    private Gender gender;

    @NotBlank(message = "Phone is required")
    private String phone;

    @NotNull(message = "Height is required")
    @Positive(message = "Height must be positive")
    private BigDecimal heightCm;

    @NotNull(message = "Weight is required")
    @Positive(message = "Weight must be positive")
    private BigDecimal weightKg;

    @NotBlank(message = "Emergency contact is required")
    private String emergencyContact;

    @NotBlank(message = "City is required")
    private String city;

    @NotBlank(message = "State is required")
    private String state;

    @NotBlank(message = "Pincode is required")
    private String pincode;

    private PatientStatus status;
}