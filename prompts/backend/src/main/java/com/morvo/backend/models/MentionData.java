// ============================================
// 3. MENTION DATA ENTITY
// ============================================
// File: src/main/java/com/morvo/backend/models/MentionData.java
package com.morvo.backend.models;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.UUID;

@Entity
@Table(name = "almarai_mentions_examples")
public class MentionData {
    @Id
    @GeneratedValue
    private UUID id;
    
    @Column(name = "mention_id", nullable = false)
    private String mentionId;
    
    @Column(name = "mention_text", nullable = false, columnDefinition = "TEXT")
    private String mentionText;
    
    @Column(nullable = false)
    private String sentiment;
    
    @Column(name = "sentiment_score", nullable = false, precision = 3, scale = 2)
    private BigDecimal sentimentScore;
    
    @Column(nullable = false)
    private String platform;
    
    @Column(nullable = false)
    private String author;
    
    @Column(name = "author_followers")
    private Integer authorFollowers;
    
    @Column(name = "author_verified")
    private Boolean authorVerified = false;
    
    @Column(nullable = false, columnDefinition = "TEXT")
    private String url;
    
    @Column(name = "published_date", nullable = false)
    private OffsetDateTime publishedDate;
    
    @Column(name = "collected_date")
    private OffsetDateTime collectedDate;
    
    private Integer reach;
    
    private Integer engagement;
    
    @Column(nullable = false)
    private String language = "ar";
    
    private String country = "SA";
    
    @Column(name = "project_id", nullable = false)
    private String projectId = "almarai_ksa";
    
    @Column(name = "source_platform", nullable = false)
    private String sourcePlatform = "brand24_demo";
    
    @Column(name = "is_active")
    private Boolean isActive = true;
    
    @Column(name = "created_at")
    private OffsetDateTime createdAt;
    
    @Column(columnDefinition = "jsonb")
    private String metadata;

    // Constructors
    public MentionData() {}

    // Getters and Setters
    public UUID getId() { return id; }
    public void setId(UUID id) { this.id = id; }
    
    public String getMentionId() { return mentionId; }
    public void setMentionId(String mentionId) { this.mentionId = mentionId; }
    
    public String getMentionText() { return mentionText; }
    public void setMentionText(String mentionText) { this.mentionText = mentionText; }
    
    public String getSentiment() { return sentiment; }
    public void setSentiment(String sentiment) { this.sentiment = sentiment; }
    
    public BigDecimal getSentimentScore() { return sentimentScore; }
    public void setSentimentScore(BigDecimal sentimentScore) { this.sentimentScore = sentimentScore; }
    
    public String getPlatform() { return platform; }
    public void setPlatform(String platform) { this.platform = platform; }
    
    public String getAuthor() { return author; }
    public void setAuthor(String author) { this.author = author; }
    
    public Integer getAuthorFollowers() { return authorFollowers; }
    public void setAuthorFollowers(Integer authorFollowers) { this.authorFollowers = authorFollowers; }
    
    public Boolean getAuthorVerified() { return authorVerified; }
    public void setAuthorVerified(Boolean authorVerified) { this.authorVerified = authorVerified; }
    
    public String getUrl() { return url; }
    public void setUrl(String url) { this.url = url; }
    
    public OffsetDateTime getPublishedDate() { return publishedDate; }
    public void setPublishedDate(OffsetDateTime publishedDate) { this.publishedDate = publishedDate; }
    
    public OffsetDateTime getCollectedDate() { return collectedDate; }
    public void setCollectedDate(OffsetDateTime collectedDate) { this.collectedDate = collectedDate; }
    
    public Integer getReach() { return reach; }
    public void setReach(Integer reach) { this.reach = reach; }
    
    public Integer getEngagement() { return engagement; }
    public void setEngagement(Integer engagement) { this.engagement = engagement; }
    
    public String getLanguage() { return language; }
    public void setLanguage(String language) { this.language = language; }
    
    public String getCountry() { return country; }
    public void setCountry(String country) { this.country = country; }
    
    public String getProjectId() { return projectId; }
    public void setProjectId(String projectId) { this.projectId = projectId; }
    
    public String getSourcePlatform() { return sourcePlatform; }
    public void setSourcePlatform(String sourcePlatform) { this.sourcePlatform = sourcePlatform; }
    
    public Boolean getIsActive() { return isActive; }
    public void setIsActive(Boolean isActive) { this.isActive = isActive; }
    
    public OffsetDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(OffsetDateTime createdAt) { this.createdAt = createdAt; }
    
    public String getMetadata() { return metadata; }
    public void setMetadata(String metadata) { this.metadata = metadata; }
}
