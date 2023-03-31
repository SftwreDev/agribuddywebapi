"""
    Source codes for MATLAB

"""


"""
    % Codes for regression analysis of weather forecast and dates


    
        clc; clear all; close all;

        x = datenum('31-Mar-2023'):datenum('04-Apr-2023');
        y = [10 7 5 3 2];

        plot(x,y,'o','MarkerSize',10)

        a = polyfit(x,y,1)

        % the polynomial equation becomes y = 1.000 x = 0.0000
        y_hat = polyval(a,x)
        hold on 
        plot(x,y_hat)

        xlabel('5 Days Forecast')
        ylabel('Predicted Wind Speed')
        title("Regression Analysis for Wind Speed")
        legend("measured","predicted")

        %error

        Error = y_hat - y;
        REMS = sqrt(mean(Error.^2))

"""



"""
    Source codes for curve fitting


    clc; clear all; close all;

    x = [ Insert numpy array of datasets here  ];
    y = [  Insert numpy array of datasets here ]


    plot(x,y,'o','MarkerSize',10)

    %use curve fitting toolbox
    cftool

"""