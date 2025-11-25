#include "TFile.h"
#include "TTree.h"
#include "TCanvas.h"
#include "TGraph.h"
#include "TMultiGraph.h"
#include "TAxis.h"
#include "TLegend.h"
#include "TH1F.h"
#include "TROOT.h"
#include <iostream>
#include <vector>
#include <algorithm>
#include <string>
#include <regex>

// ADC to mV conversion factors
const float ADC_TO_MV_B4 = 2000.0 / (4096.0 - 1.0);
const float ADC_TO_MV_B1 = 2000.0 / (16384.0 - 1.0);

// Function to calculate the baseline (median of first 100 samples)
float get_baseline(const unsigned short* waveform, int n_samples) {
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

void compare_waveforms() {
    // File 1
    TFile *f1 = TFile::Open("data_30ton/majority_test_251027T0850_46.root");
    TTree *t1 = (TTree*)f1->Get("daq");
    unsigned short waveform1[240];
    unsigned int event_id1;
    t1->SetBranchAddress("adc_b4_ch9", waveform1);
    t1->SetBranchAddress("event_id", &event_id1);

    // File 2
    TFile *f2 = TFile::Open("data_30ton/majority_test_251016T0809_33.root");
    TTree *t2 = (TTree*)f2->Get("daq");
    unsigned short waveform2[240];
    unsigned int event_id2; // Need to read event_id for file 2 as well
    t2->SetBranchAddress("adc_b4_ch9", waveform2);
    t2->SetBranchAddress("event_id", &event_id2);

    int triggered_events_file1 = 0;
    for (int i = 0; i < t1->GetEntries(); i++) {
        t1->GetEntry(i);
        
        float baseline1 = get_baseline(waveform1, 240);
        bool trigger = false;
        for (int j = 0; j < 240; j++) {
            if (-(waveform1[j] - baseline1) * ADC_TO_MV_B4 > 1000) {
                trigger = true;
                break;
            }
        }

        if (trigger) {
            triggered_events_file1++;
            TCanvas *c = new TCanvas("c", "", 1200, 800);
            TGraph *g1 = new TGraph(240);
            g1->SetTitle((std::string("Event ") + std::to_string(event_id1) + " (b4ch9 triggered > 1V) from File 1;Sample;mV").c_str());
            for(int j=0; j<240; j++) g1->SetPoint(j, j, -(waveform1[j] - baseline1) * ADC_TO_MV_B4);
            g1->SetLineColor(kBlue);
            g1->Draw("AL");
            c->SaveAs((std::string("waveform_comparison_b4ch9_triggered/event_") + std::to_string(event_id1) + "_file1.png").c_str());
            delete c;
            delete g1;
        }
    }
    std::cout << "compare_waveforms: Saved " << triggered_events_file1 << " plots for File 1." << std::endl;
    delete f1;

    int triggered_events_file2 = 0;
    for (int i = 0; i < t2->GetEntries(); i++) {
        t2->GetEntry(i);
        
        float baseline2 = get_baseline(waveform2, 240);
        bool trigger = false;
        for (int j = 0; j < 240; j++) {
            if (-(waveform2[j] - baseline2) * ADC_TO_MV_B4 > 1000) {
                trigger = true;
                break;
            }
        }

        if (trigger) {
            triggered_events_file2++;
            TCanvas *c = new TCanvas("c", "", 1200, 800);
            TGraph *g2 = new TGraph(240);
            g2->SetTitle((std::string("Event ") + std::to_string(event_id2) + " (b4ch9 triggered > 1V) from File 2;Sample;mV").c_str());
            for(int j=0; j<240; j++) g2->SetPoint(j, j, -(waveform2[j] - baseline2) * ADC_TO_MV_B4);
            g2->SetLineColor(kRed);
            g2->Draw("AL");
            c->SaveAs((std::string("waveform_comparison_b4ch9_triggered/event_") + std::to_string(event_id2) + "_file2.png").c_str());
            delete c;
            delete g2;
        }
    }
    std::cout << "compare_waveforms: Saved " << triggered_events_file2 << " plots for File 2." << std::endl;
    delete f2;
}

void plot_b1ch1_triggered_on_b4ch9_bu(const std::vector<std::string>& filenames) {
    int total_triggered_events = 0;
    for (const auto& filename : filenames) {
        TFile *f = TFile::Open(filename.c_str());
        if (!f || f->IsZombie()) continue;
        TTree *t = (TTree*)f->Get("daq");
        if (!t) continue;

        unsigned short trigger_waveform[240];
        unsigned short plot_waveform[1920];
        unsigned int event_id;
        t->SetBranchAddress("adc_b4_ch9", trigger_waveform);
        t->SetBranchAddress("adc_b1_ch1", plot_waveform);
        t->SetBranchAddress("event_id", &event_id);

        // Extract filename suffix for plot naming
        std::regex re(".*majority_test_251028T1854_(\\d+).root");
        std::smatch match;
        std::string filename_suffix = "unknown";
        if (std::regex_search(filename, match, re) && match.size() > 1) {
            filename_suffix = match.str(1);
        }

        for (int i = 0; i < t->GetEntries(); i++) {
            t->GetEntry(i);
            
            float trigger_baseline = get_baseline(trigger_waveform, 240);
            bool trigger = false;
            for (int j = 0; j < 240; j++) {
                if (-(trigger_waveform[j] - trigger_baseline) * ADC_TO_MV_B4 > 1000) {
                    trigger = true;
                    break;
                }
            }

            if (trigger) {
                total_triggered_events++;
                float plot_baseline = get_baseline(plot_waveform, 1920);
                TCanvas *c = new TCanvas("c", "", 1200, 800);
                TGraph *g = new TGraph(1920);
                g->SetTitle((std::string("Event ") + std::to_string(event_id) + " (b4ch9 triggered > 1V) from file " + filename_suffix + ";Sample;mV").c_str());
                for(int j=0; j<1920; j++) g->SetPoint(j, j, -(plot_waveform[j] - plot_baseline) * ADC_TO_MV_B1);
                g->SetLineColor(kBlue);
                g->Draw("AL");
                c->SaveAs((std::string("b1ch1_waveforms_b4ch9_triggered/event_") + std::to_string(event_id) + "_from_" + filename_suffix + ".png").c_str());
                delete c;
                delete g;
            }
        }
        delete f;
    }
    std::cout << "plot_b1ch1_triggered_on_b4ch9: Saved " << total_triggered_events << " plots." << std::endl;
}

void plot_b1ch1_triggered_on_b4ch20(const std::vector<std::string>& filenames) {
    int total_triggered_events = 0;
    for (const auto& filename : filenames) {
        TFile *f = TFile::Open(filename.c_str());
        if (!f || f->IsZombie()) continue;
        TTree *t = (TTree*)f->Get("daq");
        if (!t) continue;

        unsigned short trigger_waveform[240];
        unsigned short plot_waveform[1920];
        unsigned int event_id;
        t->SetBranchAddress("adc_b4_ch9", trigger_waveform);
        t->SetBranchAddress("adc_b1_ch1", plot_waveform);
        t->SetBranchAddress("event_id", &event_id);

        // Extract filename suffix for plot naming
        std::regex re(".*majority_test_251030T1631_(\\d+).root");
        std::smatch match;
        std::string filename_suffix = "unknown";
        if (std::regex_search(filename, match, re) && match.size() > 1) {
            filename_suffix = match.str(1);
        }

        for (int i = 0; i < t->GetEntries(); i++) {
            t->GetEntry(i);
            
            float trigger_baseline = get_baseline(trigger_waveform, 240);
            bool trigger = false;
            for (int j = 0; j < 240; j++) {
                if (-(trigger_waveform[j] - trigger_baseline) * ADC_TO_MV_B4 > 1000) {
                    trigger = true;
                    break;
                }
            }

            if (trigger) {
                total_triggered_events++;
                float plot_baseline = get_baseline(plot_waveform, 1920);
                TCanvas *c = new TCanvas("c", "", 1200, 800);
                TGraph *g = new TGraph(1920);
                g->SetTitle((std::string("Event ") + std::to_string(event_id) + " (b4ch9 triggered > 1V) from file " + filename_suffix + ";Sample;mV").c_str());
                for(int j=0; j<1920; j++) g->SetPoint(j, j, -(plot_waveform[j] - plot_baseline) * ADC_TO_MV_B1);
                g->SetLineColor(kBlue);
                g->Draw("AL");
                c->SaveAs((std::string("test2_b1ch1_waveforms_b4ch20_triggered/event_") + std::to_string(event_id) + "_from_" + filename_suffix + ".png").c_str());
                delete c;
                delete g;
            }
        }
        delete f;
    }
    std::cout << "plot_b1ch1_triggered_on_b4ch9: Saved " << total_triggered_events << " plots." << std::endl;
}

void plot_b4ch20_triggered_on_b3ch4(const std::vector<std::string>& filenames) {
    int total_triggered_events = 0;
    for (const auto& filename : filenames) {
        TFile *f = TFile::Open(filename.c_str());
        if (!f || f->IsZombie()) continue;
        TTree *t = (TTree*)f->Get("daq");
        if (!t) continue;

        unsigned short trigger_waveform[1920];
        unsigned short plot_waveform[240];
        unsigned int event_id;
        t->SetBranchAddress("adc_b1_ch1", trigger_waveform);
        t->SetBranchAddress("adc_b4_ch9", plot_waveform);
        t->SetBranchAddress("event_id", &event_id);

        // Extract filename suffix for plot naming
        std::regex re(".*majority_test_251030T1631_(\\d+).root");
        std::smatch match;
        std::string filename_suffix = "unknown";
        if (std::regex_search(filename, match, re) && match.size() > 1) {
            filename_suffix = match.str(1);
        }

        for (int i = 0; i < t->GetEntries(); i++) {
            t->GetEntry(i);

            float trigger_baseline = get_baseline(trigger_waveform, 1920);
            bool trigger = false;
            for (int j = 0; j < 1920; j++) {
                if (-(trigger_waveform[j] - trigger_baseline) * ADC_TO_MV_B1 > 10) {
                    trigger = true;
                    break;
                }
            }

            if (trigger) {
                total_triggered_events++;
                float plot_baseline = get_baseline(plot_waveform, 240);
                TCanvas *c = new TCanvas("c", "", 1200, 800);
                TGraph *g = new TGraph(240);
                g->SetTitle((std::string("Event ") + std::to_string(event_id) + " (b4ch9 triggered > 1V) from file " + filename_suffix + ";Sample;mV").c_str());
                for(int j=0; j<240; j++) g->SetPoint(j, j, -(plot_waveform[j] - plot_baseline) * ADC_TO_MV_B1);
                g->SetLineColor(kBlue);
                g->Draw("AL");
                c->SaveAs((std::string("test2_b4ch20_waveforms_b3ch4_triggered/event_") + std::to_string(event_id) + "_from_" + filename_suffix + ".png").c_str());
                delete c;
                delete g;
            }
        }
        delete f;
    }
    std::cout << "plot_b1ch1_triggered_on_b4ch9: Saved " << total_triggered_events << " plots." << std::endl;
}


void plot_b3ch4_triggered_on_b1ch1(const std::vector<std::string>& filenames) {
    int total_triggered_events = 0;
    for (const auto& filename : filenames) {
        TFile *f = TFile::Open(filename.c_str());
        if (!f || f->IsZombie()) continue;
        TTree *t = (TTree*)f->Get("daq");
        if (!t) continue;

        unsigned short trigger_waveform[1920];
        unsigned short plot_waveform[1920];
        unsigned int event_id;
        t->SetBranchAddress("adc_b1_ch1", trigger_waveform);
        t->SetBranchAddress("adc_b3_ch4", plot_waveform);
        t->SetBranchAddress("event_id", &event_id);

        // Extract filename suffix for plot naming
        std::regex re(".*majority_test_251030T1631_(\\d+).root");
        std::smatch match;
        std::string filename_suffix = "unknown";
        if (std::regex_search(filename, match, re) && match.size() > 1) {
            filename_suffix = match.str(1);
        }

        for (int i = 0; i < t->GetEntries(); i++) {
            t->GetEntry(i);
            
            float trigger_baseline = get_baseline(trigger_waveform, 1920);
            bool trigger = false;
            for (int j = 0; j < 1920; j++) {
                if (-(trigger_waveform[j] - trigger_baseline) * ADC_TO_MV_B1 > 15) { // 15mV threshold
                    trigger = true;
                    break;
                }
            }

            if (trigger) {
                total_triggered_events++;
                float plot_baseline = get_baseline(plot_waveform, 1920);
                TCanvas *c = new TCanvas("c", "", 1200, 800);
                TGraph *g = new TGraph(1920);
                g->SetTitle((std::string("Event ") + std::to_string(event_id) + " (b1ch1 triggered > 15mV) from file " + filename_suffix + ";Sample;mV").c_str());
                for(int j=0; j<1920; j++) g->SetPoint(j, j, -(plot_waveform[j] - plot_baseline) * ADC_TO_MV_B1);
                g->SetLineColor(kBlue);
                g->Draw("AL");
                c->SaveAs((std::string("b3ch4_waveforms_b1ch1_triggered/event_") + std::to_string(event_id) + "_from_" + filename_suffix + ".png").c_str());
                delete c;
                delete g;
            }
        }
        delete f;
    }
    std::cout << "plot_b1ch1_triggered_on_b1ch1: Saved " << total_triggered_events << " plots." << std::endl;
}

void plot_b1ch1_triggered_on_b3ch4(const std::vector<std::string>& filenames) {
    int total_triggered_events = 0;
    for (const auto& filename : filenames) {
        TFile *f = TFile::Open(filename.c_str());
        if (!f || f->IsZombie()) continue;
        TTree *t = (TTree*)f->Get("daq");
        if (!t) continue;

        unsigned short trigger_waveform[1920];
        unsigned short plot_waveform[1920];
        unsigned int event_id;
        t->SetBranchAddress("adc_b3_ch4", trigger_waveform);
        t->SetBranchAddress("adc_b1_ch1", plot_waveform);
        t->SetBranchAddress("event_id", &event_id);

        // Extract filename suffix for plot naming
        std::regex re(".*majority_test_251030T1631_(\\d+).root");
        std::smatch match;
        std::string filename_suffix = "unknown";
        if (std::regex_search(filename, match, re) && match.size() > 1) {
            filename_suffix = match.str(1);
        }

        for (int i = 0; i < t->GetEntries(); i++) {
            t->GetEntry(i);

            float trigger_baseline = get_baseline(trigger_waveform, 1920);
            bool trigger = false;
            for (int j = 0; j < 1920; j++) {
                if (-(trigger_waveform[j] - trigger_baseline) * ADC_TO_MV_B1 > 1000) { // 15mV threshold
                    trigger = true;
                    break;
                }
            }

            if (trigger) {
                total_triggered_events++;
                float plot_baseline = get_baseline(plot_waveform, 1920);
                TCanvas *c = new TCanvas("c", "", 1200, 800);
                TGraph *g = new TGraph(1920);
                g->SetTitle((std::string("Event ") + std::to_string(event_id) + " (b1ch1 triggered > 15mV) from file " + filename_suffix + ";Sample;mV").c_str());
                for(int j=0; j<1920; j++) g->SetPoint(j, j, -(plot_waveform[j] - plot_baseline) * ADC_TO_MV_B1);
                g->SetLineColor(kBlue);
                g->Draw("AL");
                c->SaveAs((std::string("b1ch1_waveforms_b3ch4_triggered/event_") + std::to_string(event_id) + "_from_" + filename_suffix + ".png").c_str());
                delete c;
                delete g;
            }
        }
        delete f;
    }
    std::cout << "plot_b1ch1_triggered_on_b1ch1: Saved " << total_triggered_events << " plots." << std::endl;
}


void plot_integrated_sum(const std::vector<std::string>& filenames, bool trigger_on_b4ch9) {
    TH1F *h_integrated_sum = new TH1F("h_integrated_sum", "", 100, 0, 1.2e6);
    std::string output_filename;

    if(trigger_on_b4ch9) {
        h_integrated_sum->SetTitle("Integrated Sum of b1ch2-11 (triggered on b4ch9 > 1V);Integrated Sum (mV);Events");
        output_filename = "integrated_sum_histograms/integrated_sum_b4ch9_trigger.png";
    } else {
        h_integrated_sum->SetTitle("Integrated Sum of b1ch2-11 (triggered on b1ch1 > 30mV);Integrated Sum (mV);Events");
        output_filename = "integrated_sum_histograms/integrated_sum_b1ch1_trigger.png";
    }

    for (const auto& filename : filenames) {
        TFile *f = TFile::Open(filename.c_str());
        if (!f || f->IsZombie()) continue;
        TTree *t = (TTree*)f->Get("daq");
        if (!t) continue;

        unsigned short trigger_waveform_b1[1920];
        unsigned short trigger_waveform_b4[240];
        unsigned short waveforms[10][1920];
        
        if(trigger_on_b4ch9) {
            t->SetBranchAddress("adc_b4_ch9", trigger_waveform_b4);
        } else {
            t->SetBranchAddress("adc_b1_ch1", trigger_waveform_b1);
        }
        t->SetBranchAddress("adc_b1_ch2", waveforms[0]);
        t->SetBranchAddress("adc_b1_ch3", waveforms[1]);
        t->SetBranchAddress("adc_b1_ch4", waveforms[2]);
        t->SetBranchAddress("adc_b1_ch5", waveforms[3]);
        t->SetBranchAddress("adc_b1_ch6", waveforms[4]);
        t->SetBranchAddress("adc_b1_ch7", waveforms[5]);
        t->SetBranchAddress("adc_b1_ch8", waveforms[6]);
        t->SetBranchAddress("adc_b1_ch9", waveforms[7]);
        t->SetBranchAddress("adc_b1_ch10", waveforms[8]);
        t->SetBranchAddress("adc_b1_ch11", waveforms[9]);

        for (int i = 0; i < t->GetEntries(); i++) {
            t->GetEntry(i);
            
            bool trigger = false;
            if(trigger_on_b4ch9) {
                float trigger_baseline = get_baseline(trigger_waveform_b4, 240);
                for (int j = 0; j < 240; j++) {
                    if (-(trigger_waveform_b4[j] - trigger_baseline) * ADC_TO_MV_B4 > 1000) {
                        trigger = true;
                        break;
                    }
                }
            } else {
                float trigger_baseline = get_baseline(trigger_waveform_b1, 1920);
                for (int j = 0; j < 1920; j++) {
                    if (-(trigger_waveform_b1[j] - trigger_baseline) * ADC_TO_MV_B1 > 30) {
                        trigger = true;
                        break;
                    }
                }
            }

            if (trigger) {
                double integrated_sum = 0;
                for (int ch = 0; ch < 10; ch++) {
                    float baseline = get_baseline(waveforms[ch], 1920);
                    for (int j = 0; j < 1920; j++) {
                        integrated_sum += -(waveforms[ch][j] - baseline) * ADC_TO_MV_B1;
                    }
                }
                h_integrated_sum->Fill(integrated_sum);
            }
        }
        delete f;
    }

    TCanvas *c3 = new TCanvas("c3", "Integrated Sum", 1200, 800);
    c3->cd();
    h_integrated_sum->Draw();
    c3->SaveAs(output_filename.c_str());
    std::cout << "plot_integrated_sum (triggered on " << (trigger_on_b4ch9 ? "b4ch9" : "b1ch1") << "): Saved histogram with " << h_integrated_sum->GetEntries() << " entries." << std::endl;
    delete c3;
    delete h_integrated_sum;
}

void analysis() {
    gROOT->SetBatch(kTRUE);
    //compare_waveforms();

    std::vector<std::string> task2_and_integrated_sum_filenames = {
        "data_30ton/majority_test_251030T1631_1.root",
        "data_30ton/majority_test_251030T1631_11.root",
        "data_30ton/majority_test_251030T1631_12.root",
        "data_30ton/majority_test_251030T1631_13.root",
        "data_30ton/majority_test_251030T1631_14.root",
        "data_30ton/majority_test_251030T1631_15.root",
        "data_30ton/majority_test_251030T1631_16.root",
        "data_30ton/majority_test_251030T1631_17.root",
        "data_30ton/majority_test_251030T1631_18.root",
        "data_30ton/majority_test_251030T1631_19.root",

/*	    
        "data_30ton/majority_test_251028T1854_5.root",
        "data_30ton/majority_test_251028T1854_59.root",
        "data_30ton/majority_test_251028T1854_58.root",
        "data_30ton/majority_test_251028T1854_57.root",
        "data_30ton/majority_test_251028T1854_56.root",
        "data_30ton/majority_test_251028T1854_55.root",
        "data_30ton/majority_test_251028T1854_54.root",
        "data_30ton/majority_test_251028T1854_53.root",
        "data_30ton/majority_test_251028T1854_52.root",
        "data_30ton/majority_test_251028T1854_51.root",
        "data_30ton/majority_test_251028T1854_50.root"
*/
    };

    plot_b1ch1_triggered_on_b4ch20(task2_and_integrated_sum_filenames);
    plot_b4ch20_triggered_on_b3ch4(task2_and_integrated_sum_filenames);

    //plot_b1ch1_triggered_on_b4ch9(task2_and_integrated_sum_filenames);    
    //plot_b1ch1_triggered_on_b1ch1(task2_and_integrated_sum_filenames);
    //plot_b1ch1_triggered_on_b1ch9(task2_and_integrated_sum_filenames);

    //plot_integrated_sum(task2_and_integrated_sum_filenames, false); // trigger on b1ch1
    //plot_integrated_sum(task2_and_integrated_sum_filenames, true); // trigger on b4ch9
}
