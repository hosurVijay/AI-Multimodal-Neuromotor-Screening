package com.neurologicaldisorder.Controller;

import com.neurologicaldisorder.Dto.PatientReportDetails;
import com.neurologicaldisorder.Service.ReportServices;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;


@RestController
@RequestMapping("/api/report")
@RequiredArgsConstructor
public class ReportController {

    private final ReportServices reportServices;

    


    @GetMapping("/{reportId}")
    public ResponseEntity<PatientReportDetails> getPatientReportDetails(@PathVariable Integer reportId) {

        return ResponseEntity.ok(reportServices.getReportById(reportId));
    }
}
