# CivicAI - Smart City Complaint Management System

A complete AI-powered web application for managing civic complaints and improving urban infrastructure through citizen participation.

## 🎯 Project Overview

CivicAI is a Smart City platform that enables citizens to report civic problems (potholes, garbage, broken streetlights, water leaks, etc.) and allows municipal authorities to manage, prioritize, and resolve these complaints efficiently. The system uses AI to automatically categorize complaints, assign priorities, and route them to appropriate departments.

## 🌟 Problem Statement

Urban cities face numerous infrastructure problems reported by citizens, but there's no centralized, efficient system to:
- Track and manage all complaints
- Prioritize urgent issues
- Assign complaints to right departments
- Monitor resolution progress
- Provide citizens with real-time updates

CivicAI solves this by providing a unified platform for smart city management.

## ✨ Key Features

### Citizen Module
- **User Registration/Login**: Secure authentication
- **Submit Complaints**: Easy-to-use complaint form with:
  - Category selection
  - Location input (manual + GPS)
  - Photo upload
  - Detailed description
  - Auto-generated complaint ID
- **Track Complaints**: View status and updates in real-time
- **View Details**: See full complaint information and admin remarks

### AI-Powered Complaint Analysis
- **Automatic Categorization**: AI identifies complaint type
- **Priority Assignment**: Low, Medium, High, Critical
- **Department Routing**: Auto-assigns to appropriate department
- **Reason Explanation**: AI provides reasoning for priority
- **Duplicate Detection**: Identifies similar complaints
- **Fallback System**: Works without Gemini API

### Admin Dashboard
- **Real-time Statistics**: Total, pending, in-progress, resolved complaints
- **Complaint Management**: Search, filter, view all complaints
- **Status Updates**: Change complaint status through workflow
- **Department Assignment**: Assign/reassign complaints
- **Add Remarks**: Provide updates and instructions
- **Upload Resolution Proof**: Add before/after images
- **Analytics Dashboard**: Charts and insights

### Smart City Map
- **Interactive Map**: Leaflet.js + OpenStreetMap
- **Complaint Markers**: Display complaints with priorities
- **Heatmap**: Visualize problem density
- **Click to Select**: Set location by clicking on map
- **Real-time Updates**: Shows live complaint locations

### Analytics & Insights
- **Complaint Trends**: Charts for categories, priorities, status
- **Department Workload**: Shows which departments are busiest
- **Resolution Metrics**: Average time to resolve
- **High-Priority Alerts**: Identifies critical issues
- **Department Statistics**: Complaints by department

### CivicAI Chatbot
- 24/7 assistance with questions about:
  - How to report issues
  - Complaint status checking
  - System features
  - Department information
- Rule-based responses (Gemini API optional)
- Persistent chat history

### UI/UX
- Modern, clean design with blue/green accents
- Responsive on mobile, tablet, desktop
- Professional dashboard interface
- Bootstrap Icons integration
- Smooth animations and transitions
- Intuitive navigation

## 🏗️ Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Backend**: Python Flask
- **Database**: SQLite
- **Maps**: Leaflet.js + OpenStreetMap
- **Charts**: Chart.js
- **Icons**: Bootstrap Icons
- **Security**: Password hashing, session management
- **AI**: Google Gemini API (optional) + Rule-based fallback

## 📁 Project Structure
