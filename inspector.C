
void inspector() {
  TFile f("data_30ton/majority_test_251027T0850_46.root");
  TTree* t = (TTree*) f.Get("daq");
  t->Print();
}
