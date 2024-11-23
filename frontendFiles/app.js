const app = angular.module('app', ['ui.router']);
var baseUrl = 'http://127.0.0.1:8000';

app.config(['$urlRouterProvider', '$stateProvider', function($urlRouterProvider, $stateProvider) {
    $urlRouterProvider.otherwise('/main');
    $stateProvider
        .state('main', {
            url: '/main',
            templateUrl: 'index.html',
            controller: 'MainController',
            controllerAs: 'mainCtrl'
        })
}]);

app.controller('MainController',['$http', function ($http) {
    var mainCtrl = this;
    mainCtrl.username = '';
    mainCtrl.password = '';

    mainCtrl.login = function() {
        console.log(mainCtrl.username, mainCtrl.password);
        if (mainCtrl.email && mainCtrl.password) {
            var req = {
                method: 'POST',
                url: `${baseUrl}/scrapeAttendance/`,
                withCredentials: true,
                headers: {
                    'Content-Type': "application/json"
                },
                data: {
                    "username": mainCtrl.username,
                    "password": mainCtrl.password
                }
            };
            $http(req).then(function(response) {
                console.log(response);
            }, function(error) { 
                console.log("error", error);
            });
        } 
    };

    mainCtrl.getAttendance = function() {
        var req = {
            method: 'GET',
            url: `${baseUrl}/getAttendance/`,
            withCredentials: true
        };
        $http(req).then(function(response) {
            console.log(response);
            subjects =response.data.subjects;
        }, function(error) {
            console.log(error);
        });
    };
}]);
