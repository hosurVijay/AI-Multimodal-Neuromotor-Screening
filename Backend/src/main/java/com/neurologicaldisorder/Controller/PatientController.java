package com.neurologicaldisorder.Controller;

import com.neurologicaldisorder.Dto.PatientReportDetails;
import com.neurologicaldisorder.Dto.PatientRequest;
import com.neurologicaldisorder.Dto.PatientResponse;
import com.neurologicaldisorder.Dto.PatientSummaryResponse;
import com.neurologicaldisorder.Service.PatientService;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

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



    @PostMapping("/register")
    public ResponseEntity<PatientResponse> createPatient(
            @Valid @RequestBody PatientRequest request) {

        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(patientService.createPatient(request));
    }


}