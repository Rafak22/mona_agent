// ============================================
// 1. SEO DATA ENTITY
// ============================================
// File: src/main/java/com/morvo/backend/models/SeoData.java
package com.morvo.backend.models;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.UUID;

@Entity
@Table(name = "almarai_seo_examples")
public class SeoData {
    @Id
    @GeneratedValue
    private UUID id;
    
    @Column(nullable = false)
    private String keyword;
    
    @Column(nullable = false)
    private Integer position;
    
    @Column(name = "previous_position")
    private Integer previousPosition;
    
    @Column(name = "position_change")
    private Integer positionChange;
    
    @Column(nullable = false)
    private Integer volume;
    
    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal cpc;
    
    @Column(nullable = false, precision = 3, scale = 2)
    private BigDecimal competition;
    
    @Column(nullable = false)
    private String url;
    
    @Column(name = "search_engine", nullable = false)
    private String searchEngine = "google";
    
    @Column(nullable = false)
    private String location = "Saudi Arabia";
    
    @Column(nullable = false)
    private String device = "desktop";
    
    @Column(name = "tracked_date")
    private OffsetDateTime trackedDate;
    
    @Column(name = "project_id", nullable = false)
    private String projectId = "almarai_ksa";
    
    @Column(name = "source_platform", nullable = false)
    private String sourcePlatform = "se_ranking_demo";
    
    @Column(name = "is_active")
    private Boolean isActive = true;
    
    @Column(name = "created_at")
    private OffsetDateTime createdAt;

    // Constructors
    public SeoData() {}

    // Getters and Setters
    public UUID getId() { return id; }
    public void setId(UUID id) { this.id = id; }
    
    public String getKeyword() { return keyword; }
    public void setKeyword(String keyword) { this.keyword = keyword; }
    
    public Integer getPosition() { return position; }
    public void setPosition(Integer position) { this.position = position; }
    
    public Integer getPreviousPosition() { return previousPosition; }
    public void setPreviousPosition(Integer previousPosition) { this.previousPosition = previousPosition; }
    
    public Integer getPositionChange() { return positionChange; }
    public void setPositionChange(Integer positionChange) { this.positionChange = positionChange; }
    
    public Integer getVolume() { return volume; }
    public void setVolume(Integer volume) { this.volume = volume; }
    
    public BigDecimal getCpc() { return cpc; }
    public void setCpc(BigDecimal cpc) { this.cpc = cpc; }
    
    public BigDecimal getCompetition() { return competition; }
    public void setCompetition(BigDecimal competition) { this.competition = competition; }
    
    public String getUrl() { return url; }
    public void setUrl(String url) { this.url = url; }
    
    public String getSearchEngine() { return searchEngine; }
    public void setSearchEngine(String searchEngine) { this.searchEngine = searchEngine; }
    
    public String getLocation() { return location; }
    public void setLocation(String location) { this.location = location; }
    
    public String getDevice() { return device; }
    public void setDevice(String device) { this.device = device; }
    
    public OffsetDateTime getTrackedDate() { return trackedDate; }
    public void setTrackedDate(OffsetDateTime trackedDate) { this.trackedDate = trackedDate; }
    
    public String getProjectId() { return projectId; }
    public void setProjectId(String projectId) { this.projectId = projectId; }
    
    public String getSourcePlatform() { return sourcePlatform; }
    public void setSourcePlatform(String sourcePlatform) { this.sourcePlatform = sourcePlatform; }
    
    public Boolean getIsActive() { return isActive; }
    public void setIsActive(Boolean isActive) { this.isActive = isActive; }
    
    public OffsetDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(OffsetDateTime createdAt) { this.createdAt = createdAt; }
}