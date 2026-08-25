package com.neurologicaldisorder.Service;

import com.neurologicaldisorder.Dto.PatientReportDetails;
import com.neurologicaldisorder.Dto.PatientRequest;
import com.neurologicaldisorder.Dto.PatientResponse;
import com.neurologicaldisorder.Dto.PatientSummaryResponse;
import com.neurologicaldisorder.Model.Patient;
import com.neurologicaldisorder.Model.PatientStatus;
import com.neurologicaldisorder.Model.User;
import com.neurologicaldisorder.Repository.PatientRepo;


import com.neurologicaldisorder.Repository.UserRepo;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;


import org.jspecify.annotations.Nullable;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.Period;
import java.util.List;

@Service
@RequiredArgsConstructor
public class PatientService {

    private final PatientRepo patientRepo;

    private final UserRepo userRepo;

    public List<PatientResponse> getAllPatients() {

        return patientRepo.findAll()
                .stream()
                .map(this::mapToResponse)
                .toList();
    }

    public User getUser() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        User user = (User) authentication.getPrincipal();
        return user;
    }


    public PatientResponse getPatientById(Integer patientId) {

        Patient patient = patientRepo.findById(patientId)
                .orElseThrow(() ->
                        new RuntimeException(
                                "Patient not found with id: "
                                        + patientId
                        )
                );

        return mapToResponse(patient);
    }


    private PatientResponse mapToResponse(Patient patient) {

        return PatientResponse.builder()

                .patientId(patient.getPatientId())

                .fullName(patient.getFullName())

                .profileImage(patient.getProfileImage())

                .dateOfBirth(patient.getDateOfBirth())

                .gender(patient.getGender())

                .phone(patient.getPhone())

                .heightCm(patient.getHeightCm())

                .weightKg(patient.getWeightKg())

                .emergencyContact(
                        patient.getEmergencyContact()
                )

                .city(patient.getCity())

                .state(patient.getState())

                .pincode(patient.getPincode())

                .registrationDate(
                        patient.getRegistrationDate()
                )

                .status(patient.getStatus())

                .createdAt(patient.getCreatedAt())

                .updatedAt(patient.getUpdatedAt())

                .createdByUserId(
                        patient.getCreatedBy() != null
                                ? patient.getCreatedBy().getUserId()
                                : null
                )

                .createdByUsername(
                        patient.getCreatedBy() != null
                                ? patient.getCreatedBy().getUsername()
                                : null
                )
                .age(Period.between(patient.getDateOfBirth(), LocalDate.now()).getYears())

                .build();
    }

    public PatientSummaryResponse getAllPatientSummary(Patient patient) {

        PatientSummaryResponse response = PatientSummaryResponse.builder()
                .patientId(patient.getPatientId())
                .place(patient.getCity())
                .status(patient.getStatus())
                .fullName(patient.getFullName())
                .build();

        return response;
    }

    public List<PatientSummaryResponse> getAllPatientsSummary() {
        return patientRepo.findAll()
                .stream()
                .map(this::getAllPatientSummary)
                .toList();
    }


    public List<PatientReportDetails> getReports(int patientId) {

        Patient patient = patientRepo.findById(patientId)
                .orElseThrow(() ->
                        new EntityNotFoundException(
                                "Patient not found with id: " + patientId
                        )
                );

        return patient.getReports()
                .stream()
                .map(report -> PatientReportDetails.builder()
                        .name(patient.getFullName())
                        .sessionId(report.getSessionId())
                        .reportDate(report.getReportDate())
                        .pdfUrl(report.getPdfUrl())
                        .build())
                .toList();
    }

    public PatientResponse createPatient(
            PatientRequest request) {

        Authentication authentication =
                SecurityContextHolder
                        .getContext()
                        .getAuthentication();

        String email = authentication.getName();

        User admin = userRepo.findByEmail(email)
                .orElseThrow(() ->
                        new RuntimeException(
                                "Logged-in user not found"
                        )
                );

        Patient patient = Patient.builder()
                .fullName(request.getFullName())
                .profileImage(request.getProfileImage())
                .dateOfBirth(request.getDateOfBirth())
                .gender(request.getGender())
                .phone(request.getPhone())
                .heightCm(request.getHeightCm())
                .weightKg(request.getWeightKg())
                .emergencyContact(request.getEmergencyContact())
                .city(request.getCity())
                .state(request.getState())
                .pincode(request.getPincode())

                .registrationDate(LocalDate.now())

                .status(
                        request.getStatus() != null
                                ? request.getStatus()
                                : PatientStatus.ACTIVE
                )

                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())

                .createdBy(admin)

                .build();

        Patient savedPatient =
                patientRepo.save(patient);

        return mapToResponse(savedPatient);
    }


}