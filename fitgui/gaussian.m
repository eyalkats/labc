function f = gaussian(x,a)
    f = a(1)+a(2).*exp(-a(3).*(x-a(4)).^2);
end
