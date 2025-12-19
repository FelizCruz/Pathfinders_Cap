"""
Azure Language Text Analytics client for sentiment analysis and key phrase extraction.
Uses the Azure Cognitive Services Language API.
"""
import requests
from typing import Dict, List, Optional
from .config import TextAnalyticsConfig


class TextAnalyticsClient:
    """Client for Azure Language Text Analytics API."""
    
    def __init__(self):
        """Initialize the Text Analytics client."""
        self.endpoint = TextAnalyticsConfig.ENDPOINT.rstrip('/')
        self.api_key = TextAnalyticsConfig.API_KEY
        self.api_key_2 = TextAnalyticsConfig.API_KEY_2
        self.current_key = self.api_key  # Start with primary key
        
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with current API key."""
        return {
            'Ocp-Apim-Subscription-Key': self.current_key,
            'Content-Type': 'application/json'
        }
    
    def _switch_key(self):
        """Switch to secondary API key for failover."""
        if self.current_key == self.api_key:
            self.current_key = self.api_key_2
            print("⚠ Switched to secondary API key")
        else:
            self.current_key = self.api_key
            print("⚠ Switched to primary API key")
    
    def _make_request(self, endpoint_path: str, documents: List[Dict], retry: bool = True) -> Optional[Dict]:
        """
        Make a request to the Text Analytics API with automatic key failover.
        
        Args:
            endpoint_path: API endpoint path
            documents: List of document objects
            retry: Whether to retry with secondary key on failure
            
        Returns:
            API response or None on failure
        """
        url = f"{self.endpoint}/language/:analyze-text?api-version=2023-04-01"
        
        try:
            response = requests.post(
                url,
                headers=self._get_headers(),
                json={
                    "kind": endpoint_path,
                    "analysisInput": {
                        "documents": documents
                    }
                }
            )
            
            if response.status_code == 401 and retry:
                # Try with secondary key
                self._switch_key()
                return self._make_request(endpoint_path, documents, retry=False)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            if retry:
                self._switch_key()
                return self._make_request(endpoint_path, documents, retry=False)
            print(f"✗ Text Analytics API error: {e}")
            return None
    
    def analyze_sentiment(self, texts: List[str]) -> List[Dict]:
        """
        Analyze sentiment of given texts.
        
        Args:
            texts: List of text strings to analyze
            
        Returns:
            List of sentiment results with scores
        """
        if not texts:
            return []
        
        documents = [
            {"id": str(i), "language": "en", "text": text[:5120]}  # API limit
            for i, text in enumerate(texts)
        ]
        
        print(f"✓ Analyzing sentiment for {len(documents)} documents...")
        
        result = self._make_request("SentimentAnalysis", documents)
        
        if not result:
            return []
        
        sentiments = []
        for doc in result.get("results", {}).get("documents", []):
            sentiments.append({
                "id": doc.get("id"),
                "sentiment": doc.get("sentiment"),
                "confidence_scores": doc.get("confidenceScores", {}),
                "sentences": [
                    {
                        "text": s.get("text", "")[:100],
                        "sentiment": s.get("sentiment"),
                        "confidence": s.get("confidenceScores", {})
                    }
                    for s in doc.get("sentences", [])
                ]
            })
        
        print(f"✓ Successfully analyzed sentiment for {len(sentiments)} documents")
        return sentiments
    
    def extract_key_phrases(self, texts: List[str]) -> List[Dict]:
        """
        Extract key phrases from given texts.
        
        Args:
            texts: List of text strings to analyze
            
        Returns:
            List of key phrase results
        """
        if not texts:
            return []
        
        documents = [
            {"id": str(i), "language": "en", "text": text[:5120]}
            for i, text in enumerate(texts)
        ]
        
        print(f"✓ Extracting key phrases from {len(documents)} documents...")
        
        result = self._make_request("KeyPhraseExtraction", documents)
        
        if not result:
            return []
        
        phrases = []
        for doc in result.get("results", {}).get("documents", []):
            phrases.append({
                "id": doc.get("id"),
                "key_phrases": doc.get("keyPhrases", [])
            })
        
        total_phrases = sum(len(p["key_phrases"]) for p in phrases)
        print(f"✓ Extracted {total_phrases} key phrases from {len(phrases)} documents")
        return phrases
    
    def detect_language(self, texts: List[str]) -> List[Dict]:
        """
        Detect the language of given texts.
        
        Args:
            texts: List of text strings to analyze
            
        Returns:
            List of language detection results
        """
        if not texts:
            return []
        
        documents = [
            {"id": str(i), "text": text[:5120]}
            for i, text in enumerate(texts)
        ]
        
        print(f"✓ Detecting language for {len(documents)} documents...")
        
        result = self._make_request("LanguageDetection", documents)
        
        if not result:
            return []
        
        languages = []
        for doc in result.get("results", {}).get("documents", []):
            detected = doc.get("detectedLanguage", {})
            languages.append({
                "id": doc.get("id"),
                "language": detected.get("name"),
                "iso_code": detected.get("iso6391Name"),
                "confidence": detected.get("confidenceScore")
            })
        
        print(f"✓ Detected languages for {len(languages)} documents")
        return languages
    
    def recognize_entities(self, texts: List[str]) -> List[Dict]:
        """
        Recognize named entities in given texts.
        
        Args:
            texts: List of text strings to analyze
            
        Returns:
            List of entity recognition results
        """
        if not texts:
            return []
        
        documents = [
            {"id": str(i), "language": "en", "text": text[:5120]}
            for i, text in enumerate(texts)
        ]
        
        print(f"✓ Recognizing entities in {len(documents)} documents...")
        
        result = self._make_request("EntityRecognition", documents)
        
        if not result:
            return []
        
        entities = []
        for doc in result.get("results", {}).get("documents", []):
            entities.append({
                "id": doc.get("id"),
                "entities": [
                    {
                        "text": e.get("text"),
                        "category": e.get("category"),
                        "subcategory": e.get("subcategory"),
                        "confidence": e.get("confidenceScore")
                    }
                    for e in doc.get("entities", [])
                ]
            })
        
        total_entities = sum(len(e["entities"]) for e in entities)
        print(f"✓ Recognized {total_entities} entities in {len(entities)} documents")
        return entities
    
    def analyze_all(self, texts: List[str]) -> Dict:
        """
        Perform all available analyses on the given texts.
        
        Args:
            texts: List of text strings to analyze
            
        Returns:
            Dictionary containing all analysis results
        """
        print("\n" + "=" * 50)
        print("  Running Full Text Analytics Suite")
        print("=" * 50 + "\n")
        
        results = {
            "sentiment": self.analyze_sentiment(texts),
            "key_phrases": self.extract_key_phrases(texts),
            "entities": self.recognize_entities(texts),
            "languages": self.detect_language(texts)
        }
        
        print("\n✓ Completed all text analytics operations")
        return results
    
    def format_results_summary(self, results: Dict) -> str:
        """
        Format analysis results into a readable summary.
        
        Args:
            results: Dictionary from analyze_all()
            
        Returns:
            Formatted summary string
        """
        summary = "\n" + "=" * 60 + "\n"
        summary += "  TEXT ANALYTICS RESULTS SUMMARY\n"
        summary += "=" * 60 + "\n\n"
        
        # Sentiment Summary
        summary += "📊 SENTIMENT ANALYSIS:\n"
        summary += "-" * 40 + "\n"
        for item in results.get("sentiment", []):
            sentiment = item.get("sentiment", "unknown")
            scores = item.get("confidence_scores", {})
            summary += f"  Document {item['id']}: {sentiment.upper()}\n"
            summary += f"    Positive: {scores.get('positive', 0):.2%}, "
            summary += f"Neutral: {scores.get('neutral', 0):.2%}, "
            summary += f"Negative: {scores.get('negative', 0):.2%}\n"
        summary += "\n"
        
        # Key Phrases Summary
        summary += "🔑 KEY PHRASES:\n"
        summary += "-" * 40 + "\n"
        all_phrases = []
        for item in results.get("key_phrases", []):
            all_phrases.extend(item.get("key_phrases", []))
        unique_phrases = list(set(all_phrases))[:15]  # Top 15 unique
        for i, phrase in enumerate(unique_phrases, 1):
            summary += f"  {i}. {phrase}\n"
        summary += "\n"
        
        # Entities Summary
        summary += "🏷️ NAMED ENTITIES:\n"
        summary += "-" * 40 + "\n"
        entity_counts = {}
        for item in results.get("entities", []):
            for entity in item.get("entities", []):
                category = entity.get("category", "Unknown")
                entity_counts[category] = entity_counts.get(category, 0) + 1
        for category, count in sorted(entity_counts.items(), key=lambda x: -x[1]):
            summary += f"  {category}: {count} found\n"
        summary += "\n"
        
        return summary


def test_text_analytics():
    """Test the Text Analytics client with sample data."""
    client = TextAnalyticsClient()
    
    test_texts = [
        "The stock market showed strong gains today as investors responded positively to the Federal Reserve's decision.",
        "Climate change concerns are growing as extreme weather events become more frequent worldwide.",
        "The presidential election polls show a tight race between the leading candidates."
    ]
    
    print("\n" + "=" * 60)
    print("  TESTING AZURE TEXT ANALYTICS")
    print("=" * 60 + "\n")
    
    # Run all analyses
    results = client.analyze_all(test_texts)
    
    # Print formatted summary
    print(client.format_results_summary(results))
    
    return results


if __name__ == "__main__":
    test_text_analytics()
