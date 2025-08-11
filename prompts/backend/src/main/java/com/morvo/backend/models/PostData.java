// ============================================
// 2. POST DATA ENTITY
// ============================================
// File: src/main/java/com/morvo/backend/models/PostData.java
package com.morvo.backend.models;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.UUID;

@Entity
@Table(name = "almarai_posts_examples")
public class PostData {
    @Id
    @GeneratedValue
    private UUID id;
    
    @Column(name = "post_id", nullable = false)
    private String postId;
    
    @Column(name = "post_content", nullable = false, columnDefinition = "TEXT")
    private String postContent;
    
    @Column(nullable = false)
    private String platform;
    
    @Column(nullable = false)
    private String status = "published";
    
    @Column(nullable = false)
    private OffsetDateTime timestamp;
    
    @Column(name = "scheduled_time")
    private OffsetDateTime scheduledTime;
    
    @Column(name = "media_urls", columnDefinition = "text[]")
    private String[] mediaUrls;
    
    @Column(columnDefinition = "text[]")
    private String[] hashtags;
    
    @Column(columnDefinition = "text[]")
    private String[] mentions;
    
    @Column(name = "engagement_metrics", columnDefinition = "jsonb")
    private String engagementMetrics;
    
    private Integer reach;
    
    private Integer impressions;
    
    @Column(name = "click_through_rate", precision = 5, scale = 4)
    private BigDecimal clickThroughRate;
    
    @Column(name = "api_response", columnDefinition = "jsonb")
    private String apiResponse;
    
    @Column(name = "error_message", columnDefinition = "TEXT")
    private String errorMessage;
    
    @Column(name = "project_id", nullable = false)
    private String projectId = "almarai_ksa";
    
    @Column(name = "source_platform", nullable = false)
    private String sourcePlatform = "ayrshare_demo";
    
    @Column(name = "is_active")
    private Boolean isActive = true;
    
    @Column(name = "created_at")
    private OffsetDateTime createdAt;
    
    @Column(columnDefinition = "jsonb")
    private String metadata;

    // Constructors
    public PostData() {}

    // Getters and Setters
    public UUID getId() { return id; }
    public void setId(UUID id) { this.id = id; }
    
    public String getPostId() { return postId; }
    public void setPostId(String postId) { this.postId = postId; }
    
    public String getPostContent() { return postContent; }
    public void setPostContent(String postContent) { this.postContent = postContent; }
    
    public String getPlatform() { return platform; }
    public void setPlatform(String platform) { this.platform = platform; }
    
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    
    public OffsetDateTime getTimestamp() { return timestamp; }
    public void setTimestamp(OffsetDateTime timestamp) { this.timestamp = timestamp; }
    
    public OffsetDateTime getScheduledTime() { return scheduledTime; }
    public void setScheduledTime(OffsetDateTime scheduledTime) { this.scheduledTime = scheduledTime; }
    
    public String[] getMediaUrls() { return mediaUrls; }
    public void setMediaUrls(String[] mediaUrls) { this.mediaUrls = mediaUrls; }
    
    public String[] getHashtags() { return hashtags; }
    public void setHashtags(String[] hashtags) { this.hashtags = hashtags; }
    
    public String[] getMentions() { return mentions; }
    public void setMentions(String[] mentions) { this.mentions = mentions; }
    
    public String getEngagementMetrics() { return engagementMetrics; }
    public void setEngagementMetrics(String engagementMetrics) { this.engagementMetrics = engagementMetrics; }
    
    public Integer getReach() { return reach; }
    public void setReach(Integer reach) { this.reach = reach; }
    
    public Integer getImpressions() { return impressions; }
    public void setImpressions(Integer impressions) { this.impressions = impressions; }
    
    public BigDecimal getClickThroughRate() { return clickThroughRate; }
    public void setClickThroughRate(BigDecimal clickThroughRate) { this.clickThroughRate = clickThroughRate; }
    
    public String getApiResponse() { return apiResponse; }
    public void setApiResponse(String apiResponse) { this.apiResponse = apiResponse; }
    
    public String getErrorMessage() { return errorMessage; }
    public void setErrorMessage(String errorMessage) { this.errorMessage = errorMessage; }
    
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