
echo Cleaning ...
rm -rf .pytest_cache/
#rm -rf dist/
# rm -rf *.egg-info/
rm -rf ./aemvl_backend/tests/__pycache__
rm -rf ./aemvl_backend/__pycache__ 
rm -rf ./aemvl_backend/*.pyc
rm -rf ./aemvl_backend/*.pytest_cache
echo ... done