    <div class="navbar navbar-fixed-top">
      <div class="navbar-inner">
        <div class="container">
          <a class="btn btn-navbar" data-toggle="collapse" data-target=".nav-collapse">
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </a>
          <a class="brand" href="/">Search Cloud Files</a>
          <div class="nav-collapse">
            <ul class="nav">
              <?php
                if($_SERVER['PHP_SELF'] == '') {
                  echo '<li class="active">';
                }
                else {
                  echo '<li>';
                }
              ?>
            </ul>
          </div><!--/.nav-collapse -->
        </div>
      </div>
    </div>
