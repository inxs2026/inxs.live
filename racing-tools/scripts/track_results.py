#!/usr/bin/env python3
"""
Racing Results Tracker
Compare picks vs actual results, calculate performance metrics
"""
import json
import sys
from datetime import datetime
from pathlib import Path

class ResultsTracker:
    def __init__(self, workspace_dir):
        self.workspace = Path(workspace_dir)
        self.data_dir = self.workspace / "racing-tools" / "data"
        self.picks_dir = self.data_dir / "picks"
        self.results_dir = self.data_dir / "results"
        self.perf_dir = self.data_dir / "performance"
        
        # Create directories
        self.picks_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.perf_dir.mkdir(parents=True, exist_ok=True)
    
    def save_picks(self, date, track, picks):
        """
        Save daily picks
        picks = {
            "1": {"top_pick": "Horse Name", "second": "...", "third": "..."},
            "2": {...}
        }
        """
        filename = self.picks_dir / f"{date}_{track}_picks.json"
        with open(filename, 'w') as f:
            json.dump({
                "date": date,
                "track": track,
                "picks": picks
            }, f, indent=2)
        print(f"✅ Picks saved: {filename}")
    
    def save_results(self, date, track, results):
        """
        Save actual race results
        results = {
            "1": {"winner": "Horse Name", "second": "...", "third": "..."},
            "2": {...}
        }
        """
        filename = self.results_dir / f"{date}_{track}_results.json"
        with open(filename, 'w') as f:
            json.dump({
                "date": date,
                "track": track,
                "results": results
            }, f, indent=2)
        print(f"✅ Results saved: {filename}")
    
    def compare(self, date, track):
        """Compare picks vs results, calculate metrics"""
        picks_file = self.picks_dir / f"{date}_{track}_picks.json"
        results_file = self.results_dir / f"{date}_{track}_results.json"
        
        if not picks_file.exists():
            print(f"❌ No picks found for {date} {track}")
            return None
        
        if not results_file.exists():
            print(f"❌ No results found for {date} {track}")
            return None
        
        with open(picks_file) as f:
            picks_data = json.load(f)
        
        with open(results_file) as f:
            results_data = json.load(f)
        
        picks = picks_data["picks"]
        results = results_data["results"]
        
        # Calculate metrics
        total_races = len(picks)
        winners = 0
        hit_board = 0  # Top 3
        top_pick_wins = 0
        
        race_details = []
        
        for race_num, race_picks in picks.items():
            if race_num not in results:
                continue
            
            race_result = results[race_num]
            top_pick = race_picks.get("top_pick")
            second_pick = race_picks.get("second")
            third_pick = race_picks.get("third")
            
            winner = race_result.get("winner")
            second = race_result.get("second")
            third = race_result.get("third")
            
            # Check if top pick won
            if top_pick == winner:
                winners += 1
                top_pick_wins += 1
                hit_board += 1
                result = "🏆 TOP PICK WON"
            # Check if any pick hit the board
            elif top_pick in [second, third] or second_pick in [winner, second, third] or third_pick in [winner, second, third]:
                hit_board += 1
                if top_pick == second:
                    result = "🥈 Top pick 2nd"
                elif top_pick == third:
                    result = "🥉 Top pick 3rd"
                elif second_pick == winner:
                    result = "✅ 2nd pick WON"
                elif third_pick == winner:
                    result = "✅ 3rd pick WON"
                else:
                    result = "📊 Hit board"
            else:
                result = "❌ Missed"
            
            race_details.append({
                "race": race_num,
                "our_pick": top_pick,
                "winner": winner,
                "result": result
            })
        
        metrics = {
            "date": date,
            "track": track,
            "total_races": total_races,
            "top_pick_wins": top_pick_wins,
            "hit_board": hit_board,
            "win_pct": round((top_pick_wins / total_races) * 100, 1) if total_races > 0 else 0,
            "board_pct": round((hit_board / total_races) * 100, 1) if total_races > 0 else 0,
            "details": race_details
        }
        
        # Save performance metrics
        perf_file = self.perf_dir / f"{date}_{track}_performance.json"
        with open(perf_file, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        return metrics
    
    def print_report(self, metrics):
        """Print performance report"""
        if not metrics:
            return
        
        print("\n" + "="*60)
        print(f"🏇 PERFORMANCE REPORT - {metrics['track']} {metrics['date']}")
        print("="*60)
        print(f"\n📊 Overall Stats:")
        print(f"  Total Races: {metrics['total_races']}")
        print(f"  Top Pick Winners: {metrics['top_pick_wins']}/{metrics['total_races']}")
        print(f"  Hit Board (Top 3): {metrics['hit_board']}/{metrics['total_races']}")
        print(f"  Win %: {metrics['win_pct']}%")
        print(f"  Board %: {metrics['board_pct']}%")
        
        print(f"\n🏁 Race-by-Race:")
        for detail in metrics['details']:
            print(f"  R{detail['race']}: {detail['our_pick']:20s} → {detail['result']}")
        
        print("="*60 + "\n")


def main():
    tracker = ResultsTracker("/home/damato/.openclaw/workspace")
    
    if len(sys.argv) < 2:
        print("Usage: track_results.py <command> [args]")
        print("\nCommands:")
        print("  compare <date> <track>  - Compare picks vs results")
        print("\nExample:")
        print("  track_results.py compare 2026-02-12 GP")
        return
    
    command = sys.argv[1]
    
    if command == "compare":
        if len(sys.argv) < 4:
            print("Usage: track_results.py compare <date> <track>")
            return
        
        date = sys.argv[2]
        track = sys.argv[3]
        
        metrics = tracker.compare(date, track)
        tracker.print_report(metrics)


if __name__ == "__main__":
    main()
