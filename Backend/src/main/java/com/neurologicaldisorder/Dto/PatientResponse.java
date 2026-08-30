package com.neurologicaldisorder.Dto;

import com.neurologicaldisorder.Model.Gender;
import com.neurologicaldisorder.Model.Patient;
import com.neurologicaldisorder.Model.PatientStatus;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Setter
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

    public static PatientResponse from(Patient patient) {
        return PatientResponse.builder()
                .patientId(patient.getPatientId())
                .fullName(patient.getFullName())
                .profileImage(patient.getProfileImage())
                .dateOfBirth(patient.getDateOfBirth())
                .gender(patient.getGender())
                .phone(patient.getPhone())
                .heightCm(patient.getHeightCm())
                .weightKg(patient.getWeightKg())
                .emergencyContact(patient.getEmergencyContact())
                .city(patient.getCity())
                .state(patient.getState())
                .pincode(patient.getPincode())
                .registrationDate(patient.getRegistrationDate())
                .status(patient.getStatus())
                .build();
    }
}