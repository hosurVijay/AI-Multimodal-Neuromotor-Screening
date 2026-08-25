package com.neurologicaldisorder.Service;

import com.neurologicaldisorder.Dto.PatientReportDetails;
import com.neurologicaldisorder.Model.Report;
import com.neurologicaldisorder.Repository.ReportRepo;
import lombok.RequiredArgsConstructor;
import org.jspecify.annotations.Nullable;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
@RequiredArgsConstructor
public class ReportServices {
    private final ReportRepo reportRepo;


    public @Nullable PatientReportDetails getReportById(Integer reportId) {

        Report report = reportRepo.findReportByReportId(reportId).orElse(null);


        return  PatientReportDetails.builder()
                .name(report.getPatient().getFullName())
                .sessionId(report.getSessionId())
                .reportDate(report.getReportDate())
                .pdfUrl(report.getPdfUrl())
                .build();
    }

}
