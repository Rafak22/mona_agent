package com.morvo.backend.controllers;

import com.morvo.backend.models.SeoData;
import com.morvo.backend.models.PostData;
import com.morvo.backend.models.MentionData;
import com.morvo.backend.repositories.SeoRepository;
import com.morvo.backend.repositories.PostRepository;
import com.morvo.backend.repositories.MentionRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@CrossOrigin(origins = "*")
public class DataController {
    
    @Autowired
    private SeoRepository seoRepository;
    
    @Autowired
    private PostRepository postRepository;
    
    @Autowired
    private MentionRepository mentionRepository;
    
    @GetMapping("/api/health")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("MORVO Backend is running!");
    }
    
    @GetMapping("/api/seo")
    public ResponseEntity<List<SeoData>> getSeoData() {
        try {
            List<SeoData> seoData = seoRepository.findByIsActiveTrue();
            return ResponseEntity.ok(seoData);
        } catch (Exception e) {
            // Log error and return empty list for now
            System.err.println("SEO API Error: " + e.getMessage());
            return ResponseEntity.ok(List.of());
        }
    }
    
    @GetMapping("/api/posts")
    public ResponseEntity<List<PostData>> getPostsData() {
        try {
            List<PostData> postsData = postRepository.findByIsActiveTrue();
            return ResponseEntity.ok(postsData);
        } catch (Exception e) {
            // Log error and return empty list for now
            System.err.println("Posts API Error: " + e.getMessage());
            return ResponseEntity.ok(List.of());
        }
    }
    
    @GetMapping("/api/mentions")
    public ResponseEntity<List<MentionData>> getMentionsData() {
        try {
            List<MentionData> mentionsData = mentionRepository.findByIsActiveTrue();
            return ResponseEntity.ok(mentionsData);
        } catch (Exception e) {
            // Log error and return empty list for now
            System.err.println("Mentions API Error: " + e.getMessage());
            return ResponseEntity.ok(List.of());
        }
    }
}