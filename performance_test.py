#!/usr/bin/env python3
"""
Performance testing script for the vHAL MCP server.

This script benchmarks the various optimizations and measures performance improvements.
"""
import time
import statistics
from typing import List, Callable, Any
from server import *


class PerformanceTester:
    """Performance testing utility for vHAL MCP server functions."""
    
    def __init__(self):
        self.results = {}
    
    def benchmark_function(self, func: Callable, args: tuple, name: str, runs: int = 3) -> float:
        """Benchmark a function with multiple runs and return average time."""
        times = []
        
        print(f"\n🔄 Testing {name}...")
        
        for i in range(runs):
            start_time = time.time()
            try:
                result = func(*args)
                end_time = time.time()
                duration = end_time - start_time
                times.append(duration)
                
                print(f"  Run {i+1}: {duration:.3f}s - Result length: {len(str(result)) if result else 0} chars")
                
            except Exception as e:
                print(f"  Run {i+1}: FAILED - {e}")
                times.append(float('inf'))
        
        if times and all(t != float('inf') for t in times):
            avg_time = statistics.mean(times)
            std_dev = statistics.stdev(times) if len(times) > 1 else 0
            print(f"  ✅ Average: {avg_time:.3f}s ± {std_dev:.3f}s")
            return avg_time
        else:
            print(f"  ❌ All runs failed")
            return float('inf')
    
    def run_all_tests(self):
        """Run comprehensive performance tests."""
        print("🚀 vHAL MCP Server Performance Tests")
        print("=" * 50)
        
        # Test 1: Property Database Search (should be very fast with indexing)
        print("\n1. Testing Property Database Search Performance")
        test_keywords = ["SEAT", "HVAC", "MEMORY", "TEMPERATURE", "NONEXISTENT"]
        
        for keyword in test_keywords:
            avg_time = self.benchmark_function(
                VhalPropertyDatabase.search_properties,
                (keyword,),
                f"Property search for '{keyword}'",
                runs=5
            )
            self.results[f"search_{keyword}"] = avg_time
        
        # Test 2: Relationship Analysis (should be fast with caching)
        print("\n2. Testing Relationship Analysis Performance")
        test_properties = ["SEAT_MEMORY", "HVAC_BASIC", "SEAT_POSITION"]
        
        for prop in test_properties:
            avg_time = self.benchmark_function(
                discover_related_properties,
                (prop,),
                f"Relationship analysis for '{prop}'",
                runs=3
            )
            self.results[f"relationships_{prop}"] = avg_time
        
        # Test 3: Source Code Lookup (should be fast, no network)
        print("\n3. Testing Source Code Lookup Performance")
        test_lookups = ["SEAT", "HVAC", "VEHICLE"]
        
        for lookup in test_lookups:
            avg_time = self.benchmark_function(
                lookup_android_source_code,
                (lookup,),
                f"Source lookup for '{lookup}'",
                runs=3
            )
            self.results[f"lookup_{lookup}"] = avg_time
        
        # Test 4: Documentation Scraping (network dependent, might be slow)
        print("\n4. Testing Documentation Scraping Performance")
        
        # Test single page scraping
        test_url = "https://source.android.com/docs/automotive/vhal"
        avg_time = self.benchmark_function(
            VhalDocumentationScraper.scrape_page,
            (test_url,),
            "Single page scraping",
            runs=2
        )
        self.results["single_page_scrape"] = avg_time
        
        # Test parallel scraping
        test_urls = VhalDocumentationScraper.KNOWN_PAGES[:3]  # Test with 3 pages
        avg_time = self.benchmark_function(
            VhalDocumentationScraper.scrape_pages_parallel,
            (test_urls,),
            "Parallel page scraping (3 pages)",
            runs=2
        )
        self.results["parallel_scrape"] = avg_time
        
        # Test 5: Full summarization workflow
        print("\n5. Testing Full Summarization Workflow")
        test_questions = [
            "What are seat memory properties?",
            "How does HVAC temperature control work?"
        ]
        
        for question in test_questions:
            avg_time = self.benchmark_function(
                summarize_vhal,
                (question,),
                f"Full summarization for '{question[:30]}...'",
                runs=1  # Only 1 run due to network load
            )
            self.results[f"summarize_{len(question)}"] = avg_time
        
        # Test 6: Source Code Analysis (network intensive)
        print("\n6. Testing Source Code Analysis Performance")
        test_properties = ["SEAT_MEMORY_SELECT", "HVAC_TEMPERATURE_SET"]
        
        for prop in test_properties:
            avg_time = self.benchmark_function(
                analyze_vhal_implementation,
                (prop,),
                f"Source analysis for '{prop}'",
                runs=1  # Only 1 run due to network load
            )
            self.results[f"analyze_{prop}"] = avg_time
    
    def print_summary(self):
        """Print performance test summary."""
        print("\n" + "=" * 60)
        print("📊 PERFORMANCE TEST SUMMARY")
        print("=" * 60)
        
        # Group results by category
        categories = {
            "Property Search": [k for k in self.results.keys() if k.startswith("search_")],
            "Relationship Analysis": [k for k in self.results.keys() if k.startswith("relationships_")],
            "Source Lookup": [k for k in self.results.keys() if k.startswith("lookup_")],
            "Web Scraping": [k for k in self.results.keys() if "scrape" in k],
            "Full Workflows": [k for k in self.results.keys() if k.startswith(("summarize_", "analyze_"))]
        }
        
        for category, keys in categories.items():
            if keys:
                print(f"\n{category}:")
                for key in keys:
                    time_val = self.results[key]
                    if time_val == float('inf'):
                        print(f"  {key}: FAILED")
                    elif time_val < 0.1:
                        print(f"  {key}: {time_val:.4f}s ⚡ (Very Fast)")
                    elif time_val < 1.0:
                        print(f"  {key}: {time_val:.3f}s ✅ (Fast)")
                    elif time_val < 5.0:
                        print(f"  {key}: {time_val:.3f}s ⚠️  (Moderate)")
                    else:
                        print(f"  {key}: {time_val:.3f}s 🐌 (Slow)")
        
        # Overall performance assessment
        fast_count = sum(1 for t in self.results.values() if t < 1.0 and t != float('inf'))
        total_count = len([t for t in self.results.values() if t != float('inf')])
        
        print(f"\n📈 Overall Performance: {fast_count}/{total_count} operations completed in <1s")
        
        # Recommendations
        print(f"\n💡 Performance Optimizations Applied:")
        print(f"  ✅ Property database indexing and caching")
        print(f"  ✅ Parallel web scraping with ThreadPoolExecutor")
        print(f"  ✅ LRU caching for frequent operations")
        print(f"  ✅ Optimized BeautifulSoup parsing with lxml")
        print(f"  ✅ Connection reuse with requests.Session")
        print(f"  ✅ Reduced timeouts for faster failure handling")


def main():
    """Run the performance tests."""
    tester = PerformanceTester()
    
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
    finally:
        tester.print_summary()


if __name__ == "__main__":
    main()
