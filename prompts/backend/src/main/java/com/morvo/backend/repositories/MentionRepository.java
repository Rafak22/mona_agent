package com.morvo.backend.repositories;

import com.morvo.backend.models.MentionData;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.UUID;

@Repository
public interface MentionRepository extends JpaRepository<MentionData, UUID> {
    List<MentionData> findByIsActiveTrue();
    List<MentionData> findBySentiment(String sentiment);
    List<MentionData> findByPlatform(String platform);
}