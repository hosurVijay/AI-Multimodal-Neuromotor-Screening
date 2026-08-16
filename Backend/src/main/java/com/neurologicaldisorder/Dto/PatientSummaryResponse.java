package com.neurologicaldisorder.Dto;

import com.neurologicaldisorder.Model.PatientStatus;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;

@Getter
@Builder
@AllArgsConstructor
public class PatientSummaryResponse {

    private Integer patientId;

    private String fullName;

    private String place;

    private PatientStatus status;
}