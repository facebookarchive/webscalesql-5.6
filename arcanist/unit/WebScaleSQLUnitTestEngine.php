<?php
// Copyright 2004-present Facebook. All Rights Reserved.

final class WebScaleSQLUnitTestEngine extends ArcanistBaseUnitTestEngine {
  public function run() {
    // If we are running asynchronously, mark all tests as postponed
    // and return those results.
    if ($this->getEnableAsyncTests()) {
      $results = array();
      $result = new ArcanistUnitTestResult();
      $result->setName("mysql_build");
      $result->setResult(ArcanistUnitTestResult::RESULT_POSTPONED);
      $results[] = $result;
      return $results;
    }
  }

}
