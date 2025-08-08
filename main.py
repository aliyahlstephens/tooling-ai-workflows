#!/usr/bin/env python3
"""
Main automation script for the Airtable contractor application system.
This script orchestrates all the automation processes:
1. JSON Compression
2. JSON Decompression
3. Shortlist Automation
4. LLM Evaluation
"""

import sys
import argparse
from json_compression import JSONCompressor
from json_decompression import JSONDecompressor
from shortlist_automation import ShortlistAutomation
from llm_evaluation import LLMEvaluator
from config import Config

def main():
    parser = argparse.ArgumentParser(description='Airtable Contractor Application Automation')
    parser.add_argument('action', choices=['compress', 'decompress', 'shortlist', 'evaluate', 'full-pipeline'],
                       help='Action to perform')
    parser.add_argument('--applicant-id', '-a', help='Specific applicant ID to process')
    parser.add_argument('--json-file', '-f', help='JSON file path for decompression')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Airtable Contractor Application Automation")
    print("=" * 60)
    
    try:
        if args.action == 'compress':
            compressor = JSONCompressor()
            if args.applicant_id:
                print(f"Compressing data for applicant: {args.applicant_id}")
                compressed_json = compressor.compress_applicant_data(args.applicant_id)
                print("✓ Compression completed successfully")
            else:
                print("Compressing data for all applicants...")
                results = compressor.compress_all_applicants()
                successful = sum(1 for result in results.values() if result is not None)
                print(f"✓ Compression completed: {successful}/{len(results)} successful")
        
        elif args.action == 'decompress':
            decompressor = JSONDecompressor()
            if args.json_file and args.applicant_id:
                print(f"Decompressing from file: {args.json_file} for applicant: {args.applicant_id}")
                success = decompressor.decompress_from_json_file(args.json_file, args.applicant_id)
                if success:
                    print("✓ Decompression completed successfully")
                else:
                    print("✗ Decompression failed")
            elif args.applicant_id:
                print(f"Decompressing data for applicant: {args.applicant_id}")
                success = decompressor.decompress_applicant_data(args.applicant_id)
                if success:
                    print("✓ Decompression completed successfully")
                else:
                    print("✗ Decompression failed")
            else:
                print("Decompressing data for all applicants...")
                results = decompressor.decompress_all_applicants()
                successful = sum(1 for success in results.values() if success)
                print(f"✓ Decompression completed: {successful}/{len(results)} successful")
        
        elif args.action == 'shortlist':
            automation = ShortlistAutomation()
            if args.applicant_id:
                print(f"Evaluating shortlist criteria for applicant: {args.applicant_id}")
                success = automation.shortlist_applicant(args.applicant_id)
                if success:
                    print("✓ Applicant shortlisted successfully")
                else:
                    print("✗ Applicant does not meet shortlist criteria")
            else:
                print("Evaluating shortlist criteria for all applicants...")
                results = automation.shortlist_all_applicants()
                shortlisted = sum(1 for success in results.values() if success)
                print(f"✓ Shortlist evaluation completed: {shortlisted}/{len(results)} shortlisted")
                
                # Get summary
                summary = automation.get_shortlist_summary()
                print(f"\nShortlist Summary:")
                print(f"Total shortlisted leads: {summary['total_shortlisted']}")
        
        elif args.action == 'evaluate':
            evaluator = LLMEvaluator()
            if args.applicant_id:
                print(f"Evaluating applicant with LLM: {args.applicant_id}")
                success = evaluator.update_applicant_evaluation(args.applicant_id)
                if success:
                    print("✓ LLM evaluation completed successfully")
                else:
                    print("✗ LLM evaluation failed")
            else:
                print("Evaluating all applicants with LLM...")
                results = evaluator.evaluate_all_applicants()
                evaluated = sum(1 for success in results.values() if success)
                print(f"✓ LLM evaluation completed: {evaluated}/{len(results)} successful")
                
                # Get summary
                summary = evaluator.get_evaluation_summary()
                print(f"\nEvaluation Summary:")
                print(f"Total applicants: {summary['total_applicants']}")
                print(f"Evaluated: {summary['evaluated']}")
                print(f"Average score: {summary['average_score']:.1f}/10")
        
        elif args.action == 'full-pipeline':
            print("Running full automation pipeline...")
            
            # Step 1: Compress all data
            print("\n1. Compressing applicant data...")
            compressor = JSONCompressor()
            compress_results = compressor.compress_all_applicants()
            compress_success = sum(1 for result in compress_results.values() if result is not None)
            print(f"   ✓ Compression: {compress_success}/{len(compress_results)} successful")
            
            # Step 2: Evaluate with LLM
            print("\n2. Evaluating applicants with LLM...")
            evaluator = LLMEvaluator()
            eval_results = evaluator.evaluate_all_applicants()
            eval_success = sum(1 for success in eval_results.values() if success)
            print(f"   ✓ LLM Evaluation: {eval_success}/{len(eval_results)} successful")
            
            # Step 3: Shortlist candidates
            print("\n3. Evaluating shortlist criteria...")
            automation = ShortlistAutomation()
            shortlist_results = automation.shortlist_all_applicants()
            shortlisted = sum(1 for success in shortlist_results.values() if success)
            print(f"   ✓ Shortlisting: {shortlisted}/{len(shortlist_results)} shortlisted")
            
            # Final summary
            print("\n" + "=" * 60)
            print("FULL PIPELINE COMPLETED")
            print("=" * 60)
            print(f"Total applicants processed: {len(compress_results)}")
            print(f"Data compression: {compress_success}/{len(compress_results)}")
            print(f"LLM evaluation: {eval_success}/{len(eval_results)}")
            print(f"Shortlisted: {shortlisted}/{len(shortlist_results)}")
            
            # Get detailed summaries
            eval_summary = evaluator.get_evaluation_summary()
            shortlist_summary = automation.get_shortlist_summary()
            
            print(f"\nDetailed Results:")
            print(f"- Average LLM score: {eval_summary['average_score']:.1f}/10")
            print(f"- Total shortlisted leads: {shortlist_summary['total_shortlisted']}")
        
        print("\n" + "=" * 60)
        print("Automation completed successfully!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during automation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
