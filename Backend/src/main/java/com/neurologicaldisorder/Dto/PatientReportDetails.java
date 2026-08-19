package com.neurologicaldisorder.Dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDateTime;

@Getter
@Builder
public class PatientReportDetails {

    private String  name;

    private Integer sessionId;

    private LocalDateTime reportDate;

    private String pdfUrl;

//    private LocalDateTime createdAt;
//
//    private LocalDateTime updatedAt;

}
