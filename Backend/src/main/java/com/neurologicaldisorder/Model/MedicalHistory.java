package com.neurologicaldisorder.Model;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "medical_history")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class MedicalHistory {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer medicalHistoryId;

    @OneToOne
    @JoinColumn(name = "patient_id")
    private Patient patient;

    private String neurologicalDisorder;

    private Boolean strokeHistory;

    private Boolean headInjury;

    private Boolean brainInjury;

    private Boolean diabetes;

    private Boolean hypertension;

    @Column(columnDefinition = "TEXT")
    private String medications;

    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;

}
