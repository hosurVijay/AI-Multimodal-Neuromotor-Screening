package com.neurologicaldisorder.Repository;

import com.neurologicaldisorder.Model.MedicalHistory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface MedicalHistoryRepo extends JpaRepository<MedicalHistory, Integer> {
}
