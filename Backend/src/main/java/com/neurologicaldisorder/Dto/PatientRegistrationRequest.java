package com.neurologicaldisorder.Dto;
import com.neurologicaldisorder.Model.Gender;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;

@Data
public class PatientRegistrationRequest {

    // Patient details
    private String fullName;

    private LocalDate dateOfBirth;

    private Gender gender;

    private String phone;

    private BigDecimal heightCm;

    private BigDecimal weightKg;

    private String emergencyContact;

    private String city;

    private String state;

    private String pincode;


    // Medical history
    private String neurologicalDisorder;

    private Boolean strokeHistory;

    private Boolean headInjury;

    private Boolean brainInjury;

    private Boolean diabetes;

    private Boolean hypertension;

    private String medications;
}