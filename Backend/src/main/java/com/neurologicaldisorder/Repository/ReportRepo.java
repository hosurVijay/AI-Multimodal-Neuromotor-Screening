package com.neurologicaldisorder.Repository;

import com.neurologicaldisorder.Model.Report;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface ReportRepo extends JpaRepository<Report, Integer> {

    Optional<Report> findReportByReportId(Integer reportId);
}
