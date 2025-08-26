package com.morvo.backend.repositories;

import com.morvo.backend.models.SeoData;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.UUID;

@Repository
public interface SeoRepository extends JpaRepository<SeoData, UUID> {
    List<SeoData> findByIsActiveTrue();
    List<SeoData> findByKeywordContainingIgnoreCase(String keyword);
}