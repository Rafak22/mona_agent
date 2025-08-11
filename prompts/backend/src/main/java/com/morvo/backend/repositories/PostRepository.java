package com.morvo.backend.repositories;

import com.morvo.backend.models.PostData;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.UUID;

@Repository
public interface PostRepository extends JpaRepository<PostData, UUID> {
    List<PostData> findByIsActiveTrue();
    List<PostData> findByPlatform(String platform);
}