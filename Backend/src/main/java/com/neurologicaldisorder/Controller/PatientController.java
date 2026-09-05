package com.neurologicaldisorder.Controller;

import com.neurologicaldisorder.Dto.*;
import com.neurologicaldisorder.Service.PatientService;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;

import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.List;

@CrossOrigin
@RestController
@RequestMapping("/api/patients")
@RequiredArgsConstructor
public class PatientController {

    private final PatientService patientService;

    @GetMapping
    public ResponseEntity<List<PatientResponse>> getAllPatients() {

        return ResponseEntity.ok(
                patientService.getAllPatients()
        );
    }

    @GetMapping("/{patientId}")
    public ResponseEntity<PatientResponse> getPatientById(
            @PathVariable Integer patientId) {

        return ResponseEntity.ok(
                patientService.getPatientById(patientId)
        );
    }

    @GetMapping("/summary")
    public ResponseEntity<List<PatientSummaryResponse>> getAllPatientsSummary() {

        return ResponseEntity.ok(patientService.getAllPatientsSummary());
    }
    @GetMapping ("/report/{patientId}")
    public ResponseEntity<List<PatientReportDetails>> getAllReports(@PathVariable int patientId) {
        return ResponseEntity.ok(patientService.getReports(patientId));
    }


    @PostMapping(consumes = MediaType.MULTIPART_FORM_DATA_VALUE )
    @RequestMapping("/register")
    public ResponseEntity<String> registerPatient(

            @Valid @RequestPart("patient")
            PatientRegistrationRequest patientRequest,

            @RequestPart(value = "profileImage", required = false)
            MultipartFile profileImage) throws IOException {

        patientService.registerPatient(
                patientRequest,
                profileImage
        );

        return ResponseEntity.ok(
                "Patient registered successfully"
        );
    }


}