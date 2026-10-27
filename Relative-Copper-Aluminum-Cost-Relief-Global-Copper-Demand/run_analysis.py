from analysis import run_all
from make_figures import main as make_figures
if __name__=='__main__':
    run_all()
    make_figures()
    print('COMPLETE: frozen source, purged OOS, 1000 block-shuffle refits, 2000 bootstraps, 1000 perturbations, 10 figures')
