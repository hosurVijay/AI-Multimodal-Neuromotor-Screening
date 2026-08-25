package com.neurologicaldisorder.Dto;

import com.neurologicaldisorder.Model.Gender;
import com.neurologicaldisorder.Model.PatientStatus;
import lombok.Builder;
import lombok.Getter;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Getter
@Builder
public class PatientResponse {

    private Integer patientId;

    private String fullName;

    private String profileImage;

    private LocalDate dateOfBirth;

    private Gender gender;

    private String phone;

    private BigDecimal heightCm;

    private BigDecimal weightKg;

    private String emergencyContact;

    private String city;

    private String state;

    private String pincode;

    private LocalDate registrationDate;

    private PatientStatus status;

    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;

    private Integer createdByUserId;

    private String createdByUsername;

    private int age;
}