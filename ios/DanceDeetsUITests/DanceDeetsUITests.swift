//
//  DanceDeetsUITests.swift
//  DanceDeetsUITests
//
//  Created by LambertMike on 2016/07/22.
//  Copyright © 2016年 Facebook. All rights reserved.
//

import XCTest

class DanceDeetsUITests: XCTestCase {
        
    override func setUp() {
        super.setUp()
        
        // Put setup code here. This method is called before the invocation of each test method in the class.
        
        // In UI tests it is usually best to stop immediately when a failure occurs.
        continueAfterFailure = false
        // UI tests must launch the application that they test. Doing this in setup will make sure it happens for each test method.
        let app = XCUIApplication()
        app.launchEnvironment = [ "UITest": "1" ]
        setupSnapshot(app)
        app.launch()

        // In UI tests it’s important to set the initial state - such as interface orientation - required for your tests before they run. The setUp method is a good place to do this.
    }
    
    override func tearDown() {
        // Put teardown code here. This method is called after the invocation of each test method in the class.
        super.tearDown()
    }
    
    func testExample() {
      let app = XCUIApplication()

      expectationForPredicate(NSPredicate(format: "exists == true"), evaluatedWithObject: app.otherElements["mainButton"], handler: nil)
      waitForExpectationsWithTimeout(20, handler:      {(error: Any?) -> Void in
        NSLog("C0 Error is \(error)")
        NSLog("C1 %@", app.debugDescription)
      })

      // Now wait for content to load

      expectationForPredicate(NSPredicate(format: "exists == true"), evaluatedWithObject: app.otherElements["mainButton"], handler: nil)
      waitForExpectationsWithTimeout(20, handler:      {(error: Any?) -> Void in
        NSLog("C0 Error is \(error)")
        NSLog("C1 %@", app.debugDescription)
      })


      snapshot("0")
      app.otherElements["mainButton"].tap()

      expectationForPredicate(NSPredicate(format: "exists == true"), evaluatedWithObject: app.otherElements["mainButton"], handler: nil)
      waitForExpectationsWithTimeout(20, handler:      {(error: Any?) -> Void in
        NSLog("C0 Error is \(error)")
        NSLog("C1 %@", app.debugDescription)
      })

      snapshot("1")

      app.otherElements["mainButton"].tap()

      expectationForPredicate(NSPredicate(format: "exists == true"), evaluatedWithObject: app.otherElements["mainButton"], handler: nil)
      waitForExpectationsWithTimeout(20, handler:      {(error: Any?) -> Void in
        NSLog("C0 Error is \(error)")
        NSLog("C1 %@", app.debugDescription)
      })
      snapshot("2")

    }
}
