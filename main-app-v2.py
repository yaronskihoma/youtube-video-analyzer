import streamlit as st
import os
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import isodate
import pytz
from typing import List, Dict
import re

# [Existing imports remain the same]
# ADD new import for caption handling
from youtube_transcript_api import YouTubeTranscriptApi

def get_api_key() -> str:
    """Read API key from Streamlit secrets or environment."""
    # [Existing function remains the same]

class YouTubeLiteAnalyzer:
    def __init__(self, api_key: str):
        # [Existing initialization remains the same]
        
    def calculate_quota_cost(self, max_results: int, use_captions: bool = False) -> dict:
        """Calculate estimated API quota usage."""
        search_cost = 100  
        video_details_cost = 1  
        caption_cost = 75 if use_captions else 0  
        
        total_video_costs = video_details_cost * max_results
        total_caption_costs = caption_cost * max_results if use_captions else 0
        
        total_cost = search_cost + total_video_costs + total_caption_costs
        
        return {
            'search_cost': search_cost,
            'video_details_cost': total_video_costs,
            'caption_cost': total_caption_costs,
            'total_cost': total_cost,
            'daily_limit': 10000,
            'remaining_after': 10000 - total_cost
        }

    def _get_captions(self, video_id: str) -> List[Dict]:
        """Get video captions using YouTube Transcript API."""
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return transcript
        except:
            return []

    def _analyze_captions(self, video_id: str, query_keywords: List[str]) -> List[Dict]:
        """Analyze video captions for keyword matches."""
        caption_segments = []
        captions = self._get_captions(video_id)
        
        if not captions:
            return []
            
        # Analyze each caption segment
        for i, caption in enumerate(captions):
            text = caption['text'].lower()
            start_time = caption['start']
            
            # Calculate keyword matches
            matching_words = sum(1 for word in query_keywords if word in text)
            if matching_words > 0:
                relevance_score = matching_words / len(query_keywords)
                
                caption_segments.append({
                    'type': 'transcript_match',
                    'start_time': int(start_time),
                    'duration': 5,
                    'title': f"Keyword mention: {text[:50]}...",
                    'relevance_score': relevance_score,
                    'segment_type': 'transcript_match'
                })
        
        # Sort and return top matches
        sorted_segments = sorted(caption_segments, key=lambda x: x['relevance_score'], reverse=True)
        return sorted_segments[:3]  # Return top 3 caption matches

# PART1 END

def _analyze_segments(self, video_data: Dict, query_keywords: List[str], use_captions: bool = False) -> List[Dict]:
        """
        Analyze video segments for relevance and popularity.
        Now includes optional caption analysis.
        """
        hooks = []
        search_terms = set(word.lower() for word in query_keywords)
        
        # Add opening hook
        hooks.append({
            'type': 'opening',
            'start_time': 0,
            'duration': 5,
            'url': f"{video_data['url']}&t=0s",
            'relevance_score': 1.0,
            'segment_type': 'intro',
            'title': 'Opening Hook'
        })
        
        # Get caption-based segments if enabled
        if use_captions:
            caption_segments = self._analyze_captions(video_data['video_id'], query_keywords)
            for segment in caption_segments:
                segment['url'] = f"{video_data['url']}&t={segment['start_time']}s"
                hooks.append(segment)
        
        # [Rest of existing chapter analysis remains the same until the end]
        # After adding chapter segments:
        
        # Sort all hooks by relevance score, prioritizing caption matches slightly
        hooks = sorted(hooks, key=lambda x: (
            x.get('relevance_score', 0) * 1.2 if x.get('segment_type') == 'transcript_match' 
            else x.get('relevance_score', 0)
        ), reverse=True)
        
        return hooks

    def analyze_videos(self, query: str, max_results: int = 5, 
                      duration_type: str = 'any',
                      order_by: str = 'viewCount',
                      region_code: str = 'US',
                      days_ago: int = 5,
                      use_captions: bool = False) -> List[Dict]:
        """
        Search and analyze videos with enhanced filters and segment analysis.
        Now includes caption analysis option.
        """
        try:
            with st.status("🔍 Searching videos...") as status:
                # [Existing search code remains the same until video processing]
                
                for video in videos_response['items']:
                    try:
                        # [Existing video data processing remains the same until hooks analysis]
                        
                        # Update segment analysis to include captions
                        video_data['hooks'] = self._analyze_segments(
                            video_data, 
                            query_keywords,
                            use_captions=use_captions
                        )
                        analyzed_videos.append(video_data)
                        
                    except Exception as e:
                        st.warning(f"Error processing video {video.get('id', 'unknown')}: {str(e)}")
                        continue

                status.update(label="✅ Analysis complete!", state="complete")
                return analyzed_videos
            
        except Exception as e:
            st.error(f"Error in video analysis: {str(e)}")
            return []

def display_video_segments(video: Dict):
    """Display video segments with enhanced information."""
    st.write("**🎯 Relevant Segments:**")
    
    # Updated segment types
    segments_by_type = {
        'keyword_match': '🔍 Keyword Matches',
        'engagement': '🔥 High Engagement',
        'intro': '👋 Introduction',
        'transcript_match': '📝 In Video Mentions'
    }
    
    # Group segments by type, prioritizing transcript matches
    for segment_type in ['transcript_match', 'keyword_match', 'engagement', 'intro']:
        segments = [h for h in video['hooks'] if h.get('segment_type') == segment_type]
        if segments:
            st.markdown(f"**{segments_by_type[segment_type]}:**")
            for hook in segments:
                relevance = hook.get('relevance_score', 0) * 100
                timestamp = str(timedelta(seconds=int(hook['start_time'])))
                
                # Enhanced color for transcript matches
                base_color = "rgba(0, 128, 255, 0.2)" if segment_type == 'transcript_match' else f"rgba(0, {min(255, int(relevance * 2.55))}, 0, 0.2)"
                
                st.markdown(
                    f"""
                    <div style="padding: 10px; background-color: {base_color}; border-radius: 5px; margin: 5px 0;">
                        <strong>{hook.get('title', 'Segment')}</strong><br>
                        Time: {timestamp} | Relevance: {relevance:.1f}%<br>
                        <a href="{hook['url']}" target="_blank">Watch Segment</a>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

# PART 2 END

def main():
    st.set_page_config(
        page_title="YouTube Video Analyzer",
        page_icon="🎥",
        layout="wide"
    )
    
    st.title("🎥 YouTube Video Analyzer")
    
    # API Key handling in sidebar with new caption option
    with st.sidebar:
        st.header("⚙️ Settings")
        api_key = st.text_input(
            "YouTube API Key",
            type="password",
            help="Enter your YouTube Data API v3 key"
        )
        
        # Add caption analysis toggle
        use_captions = st.checkbox(
            "Enable Caption Analysis (Beta)",
            help="Analyzes video transcripts for better keyword matching. Uses additional quota (75 units per video)"
        )
        
        if use_captions:
            st.sidebar.warning("""
            ⚠️ Caption Analysis Enabled
            - Uses 75 additional quota units per video
            - Provides deeper content analysis
            - May not work for all videos
            """)
        
        st.markdown("---")
        st.markdown("""
        ### 📖 Quick Guide
        1. Enter your API key
        2. Set search parameters
        3. Click Search
        4. Analyze results
        
        [Get API Key](https://console.cloud.google.com/apis/credentials)
        """)
    
    if not api_key:
        st.warning("⚠️ Please enter your YouTube API Key in the sidebar")
        st.info("Need an API Key? [Get one here](https://console.cloud.google.com/apis/credentials)")
        st.stop()
    
    try:
        analyzer = YouTubeLiteAnalyzer(api_key)
        
        st.header("🔍 Search Parameters")
        
        query = st.text_input("Enter search query (e.g., 'mobile game ads')")
        
        col1, col2, col3 = st.columns(3)
        
        # [Existing column 1 and 2 content remains the same]
        
        with col3:
            max_results = st.slider(
                "Number of results",
                min_value=1,
                max_value=10,
                value=5,
                help="Maximum number of videos to analyze"
            )
            
            # Updated quota display
            quota_info = analyzer.calculate_quota_cost(max_results, use_captions)
            st.info(f"""
            **📊 Quota Usage Estimate:**
            - Search: {quota_info['search_cost']} units
            - Video details: {quota_info['video_details_cost']} units
            {f"- Caption analysis: {quota_info['caption_cost']} units" if use_captions else ""}
            - Total: {quota_info['total_cost']} units
            Daily limit: {quota_info['daily_limit']} units
            """)
            
            if use_captions:
                st.caption("💡 Caption analysis provides deeper content matching but uses more quota")
        
        # Search button with enhanced status
        if st.button("🔎 Search Videos", type="primary"):
            if not query:
                st.error("❌ Please enter a search query")
                return
                
            with st.status("🔍 Analyzing videos...", expanded=True) as status:
                # Perform search with caption option
                videos = analyzer.analyze_videos(
                    query=query,
                    max_results=max_results,
                    duration_type=duration_type,
                    order_by=order_by,
                    region_code=region_code,
                    days_ago=days_ago,
                    use_captions=use_captions
                )
                
                if videos:
                    st.header("📊 Results")
                    
                    # Enhanced export - now includes segment analysis
                    if st.download_button(
                        label="📥 Export Results",
                        data=str(videos),
                        file_name="youtube_analysis.json",
                        mime="application/json"
                    ):
                        st.success("Results exported successfully!")
                    
                    # Results counter
                    st.markdown(f"Found **{len(videos)}** videos with "
                              f"**{sum(len(v.get('hooks', [])) for v in videos)}** relevant segments")
                    
                    # Display results with enhanced segment information
                    for video in videos:
                        with st.expander(f"📺 {video['title']}", expanded=True):
                            col1, col2 = st.columns([2, 1])
                            
                            # [Existing column content remains the same]
                            
                            # Enhanced segment display with caption results
                            display_video_segments(video)
                            
                            # Add source indicator for transparency
                            st.caption(
                                "💡 Segments are identified through "
                                f"{'video captions and ' if use_captions else ''}"
                                "video chapters/description analysis"
                            )
                            
                            st.markdown("---")
                else:
                    st.warning("No videos found matching your criteria")

    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.error("Please check if your API key is valid and you have quota remaining")

if __name__ == "__main__":
    main()
