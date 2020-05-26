function data = data_extractor(filename)
    A = readmatrix(filename);
    data = A(1:8192);
end