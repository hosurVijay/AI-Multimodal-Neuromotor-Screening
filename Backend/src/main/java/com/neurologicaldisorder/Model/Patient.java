package com.neurologicaldisorder.Model;

import jakarta.persistence.*;
import lombok.*;
import org.springframework.format.annotation.DateTimeFormat;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "patient")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Patient {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer patientId;

    private String fullName;

    private String profileImage;


    private LocalDate dateOfBirth;

    @Enumerated(EnumType.STRING)
    private Gender gender;

    private String phone;

    private BigDecimal heightCm;

    private BigDecimal weightKg;

    private String emergencyContact;

    private String city;

    private String state;

    private String pincode;

    private LocalDate registrationDate;

    @Enumerated(EnumType.STRING)
    private PatientStatus status;

    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "created_by_user_id")
    private User createdBy;

    @OneToOne(mappedBy = "patient",
            cascade = CascadeType.ALL,
            orphanRemoval = true)
    private MedicalHistory medicalHistory;

    @OneToMany(mappedBy = "patient",
            cascade = CascadeType.ALL)
    private List<Report> reports;

}
