package com.morvo.backend.controllers;

import org.springframework.web.bind.annotation.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.core.JdbcTemplate;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "*")
public class DataController {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @GetMapping("/seo")
    public ResponseEntity<List<Map<String, Object>>> getSeoData() {
        String sql = "SELECT * FROM almarai_seo_examples WHERE is_active = true ORDER BY tracked_date DESC LIMIT 100";
        List<Map<String, Object>> results = jdbcTemplate.queryForList(sql);
        return ResponseEntity.ok(results);
    }

    @GetMapping("/posts")
    public ResponseEntity<List<Map<String, Object>>> getPostsData() {
        String sql = "SELECT * FROM almarai_posts_examples WHERE is_active = true ORDER BY timestamp DESC LIMIT 100";
        List<Map<String, Object>> results = jdbcTemplate.queryForList(sql);
        return ResponseEntity.ok(results);
    }

    @GetMapping("/mentions")
    public ResponseEntity<List<Map<String, Object>>> getMentionsData() {
        String sql = "SELECT * FROM almarai_mentions_examples WHERE is_active = true ORDER BY published_date DESC LIMIT 100";
        List<Map<String, Object>> results = jdbcTemplate.queryForList(sql);
        return ResponseEntity.ok(results);
    }

    @GetMapping("/health")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("MORVO Backend is running!");
    }
} 