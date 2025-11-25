#include <iostream>
#include <vector>
#include <string>
#include <map>
#include <numeric>
#include <algorithm>
#include <regex> // For string manipulation

#include "TChain.h"
#include "TFile.h"
#include "TTree.h"
#include "TH1F.h"
#include "TCanvas.h"
#include "TStyle.h"
#include "TSystem.h"
#include "TPad.h" // For gPad

// ADC to mV conversion factors from analysis.C
const float ADC_TO_MV_B4 = 2000.0 / 4095.0;
const float ADC_TO_MV_B1 = 2000.0 / 16383.0;

// Function to calculate the baseline (median of first 100 samples)
float get_baseline_cpp(const unsigned short* waveform, int n_samples) {
    int n_baseline_samples = std::min(100, n_samples);
    if (n_baseline_samples == 0) return 0;
    std::vector<unsigned short> baseline_samples(waveform, waveform + n_baseline_samples);
    std::sort(baseline_samples.begin(), baseline_samples.end());
    if (n_baseline_samples % 2 == 0) {
        return (baseline_samples[n_baseline_samples / 2 - 1] + baseline_samples[n_baseline_samples / 2]) / 2.0;
    } else {
        return baseline_samples[n_baseline_samples / 2];
    }
}

// Helper function to convert "bXchY" to "bX_chY"
std::string format_channel_name(const std::string& original_name) {
    std::regex re("b(\\d)ch(\\d+)");
    std::smatch match;
    if (std::regex_search(original_name, match, re) && match.size() == 3) {
        return "b" + match.str(1) + "_ch" + match.str(2);
    }
    return original_name; // Return original if no match
}


// Function to process files
std::map<std::string, int> process_files_cpp(const char* file_pattern, const std::vector<std::string>& trigger_channels_raw, const std::vector<std::string>& signal_channels_raw, const std::string& output_prefix, TCanvas* canvas) {
    std::map<std::string, int> trigger_counts;
    
    // Format channel names for branch access
    std::vector<std::string> trigger_channels_formatted;
    for(const auto& ch : trigger_channels_raw) {
        trigger_channels_formatted.push_back(format_channel_name(ch));
    }
    std::vector<std::string> signal_channels_formatted;
    for(const auto& ch : signal_channels_raw) {
        signal_channels_formatted.push_back(format_channel_name(ch));
    }


    for (size_t i = 0; i < trigger_channels_formatted.size(); ++i) {
        const auto& trigger_ch_formatted = trigger_channels_formatted[i];
        std::cout << "Processing trigger channel: " << trigger_ch_formatted << std::endl;
        // Use original name for reporting
        std::string original_trigger_ch_name = trigger_ch_formatted;
        std::regex re("b(\\d)_ch(\\d+)");
        std::smatch match;
        if (std::regex_search(trigger_ch_formatted, match, re) && match.size() == 3) {
            original_trigger_ch_name = "b" + match.str(1) + "ch" + match.str(2);
        }
        trigger_counts[original_trigger_ch_name] = 0;


        TChain chain("daq");
        chain.Add(file_pattern);

        unsigned short trigger_waveform[240]; // Assuming trigger is always a b4 channel
        unsigned short signal_waveforms_data[10][1920];
        std::map<std::string, unsigned short*> signal_waveform_ptrs;

        chain.SetBranchAddress(("adc_" + trigger_ch_formatted).c_str(), trigger_waveform);
        for (size_t j = 0; j < signal_channels_formatted.size(); ++j) {
            signal_waveform_ptrs[signal_channels_formatted[j]] = signal_waveforms_data[j];
            chain.SetBranchAddress(("adc_" + signal_channels_formatted[j]).c_str(), signal_waveforms_data[j]);
        }

        TH1F *h_integrated_sum = new TH1F(("h_integrated_sum_" + original_trigger_ch_name + "_" + output_prefix).c_str(), ("Integrated Sum for trigger " + original_trigger_ch_name).c_str(), 1000, -500000, 500000);
        
        Long64_t nentries = chain.GetEntries();
        for (Long64_t j = 0; j < nentries; j++) {
            chain.GetEntry(j);

            float trigger_baseline = get_baseline_cpp(trigger_waveform, 240);
            bool trigger = false;
            for (int k = 0; k < 240; k++) {
                if (-(trigger_waveform[k] - trigger_baseline) * ADC_TO_MV_B4 > 1000) {
                    trigger = true;
                    break;
                }
            }

            if (trigger) {
                trigger_counts[original_trigger_ch_name]++;

                double event_integrated_sum = 0;
                for (size_t ch_idx = 0; ch_idx < signal_channels_formatted.size(); ++ch_idx) {
                    const unsigned short* current_signal_wf = signal_waveform_ptrs[signal_channels_formatted[ch_idx]];
                    float baseline = get_baseline_cpp(current_signal_wf, 1920);
                    for (int l = 0; l < 1920; l++) {
                        event_integrated_sum += -(current_signal_wf[l] - baseline) * ADC_TO_MV_B1;
                    }
                }
                h_integrated_sum->Fill(event_integrated_sum);
            }
        }

        canvas->cd(i + 1);
        gPad->SetLogy();
        h_integrated_sum->Draw();
    }

    return trigger_counts;
}

void analysis_cpp() {
    gStyle->SetOptStat(0);
    const char* set1_files = "/home/guang/work/bnl1t/drop/drop_jan26_24_pull/data_30ton/majority_test_251030T1631_1*.root";

    const char* set2_files = "/home/guang/work/bnl1t/drop/drop_jan26_24_pull/data_30ton/majority_test_251031T0706*.root";

    std::vector<std::string> trigger_channels_raw = {"b4ch9", "b4ch10", "b4ch11", "b4ch12", "b4ch18", "b4ch19", "b4ch20", "b4ch21"};
    std::vector<std::string> signal_channels_raw;
    for (int i = 2; i < 12; ++i) {
        signal_channels_raw.push_back("b1ch" + std::to_string(i));
    }

    TCanvas *c1 = new TCanvas("c1", "Set 1 Distributions", 1600, 800);
    c1->Divide(4, 2);

    std::cout << "Processing Set 1" << std::endl;
    auto set1_counts = process_files_cpp(set1_files, trigger_channels_raw, signal_channels_raw, "set1_cpp", c1);
    std::cout << "Set 1 Trigger Counts:" << std::endl;
    for(const auto& pair : set1_counts) {
        std::cout << pair.first << ": " << pair.second << std::endl;
    }

    TCanvas *c2 = new TCanvas("c2", "Set 2 Distributions", 1600, 800);
    c2->Divide(4, 2);

    std::cout << "\nProcessing Set 2" << std::endl;
    auto set2_counts = process_files_cpp(set2_files, trigger_channels_raw, signal_channels_raw, "set2_cpp", c2);
    std::cout << "Set 2 Trigger Counts:" << std::endl;
    for(const auto& pair : set2_counts) {
        std::cout << pair.first << ": " << pair.second << std::endl;
    }
}
