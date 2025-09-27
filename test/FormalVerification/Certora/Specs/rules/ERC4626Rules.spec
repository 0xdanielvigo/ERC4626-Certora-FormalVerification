using ERC20Mock as erc20Mock; // asset token
using ERC4626Mock as erc4626Mock; 

methods {
    // ERC4626 methods
    function ERC4626Mock.name() external returns string envfree;
    function ERC4626Mock.symbol() external returns string envfree;
    function ERC4626Mock.decimals() external returns uint8 envfree;
    function ERC4626Mock.asset() external returns address envfree;

    function ERC4626Mock.totalSupply() external returns uint256 envfree;
    function ERC4626Mock.balanceOf(address) external returns uint256 envfree;

    function ERC4626Mock.deposit(uint256 assets, address receiver) external returns (uint256);
    function ERC4626Mock.mint(uint256,address) external;
    function ERC4626Mock.withdraw(uint256,address,address) external;
    function ERC4626Mock.redeem(uint256,address,address) external;

    function ERC4626Mock.totalAssets() external returns uint256 envfree;
    function ERC4626Mock.convertToShares(uint256) external returns uint256 envfree;
    function ERC4626Mock.convertToAssets(uint256) external returns uint256 envfree;
    function ERC4626Mock.previewDeposit(uint256) external returns uint256 envfree;
    function ERC4626Mock.previewMint(uint256) external returns uint256 envfree;
    function ERC4626Mock.previewWithdraw(uint256) external returns uint256 envfree;
    function ERC4626Mock.previewRedeem(uint256) external returns uint256 envfree;

    function ERC4626Mock.maxDeposit(address) external returns uint256 envfree;
    function ERC4626Mock.maxMint(address) external returns uint256 envfree;
    function ERC4626Mock.maxWithdraw(address) external returns uint256 envfree;
    function ERC4626Mock.maxRedeem(address) external returns uint256 envfree;

    // ERC20 methods
    function ERC20Mock.approve(address,uint256) external returns bool;
    function ERC20Mock.transferFrom(address,address,uint256) external returns bool;
    function ERC20Mock.balanceOf(address) external returns uint256 envfree;
    function ERC20Mock.allowance(address, address) external returns uint256 envfree;

    function _.balanceOf(address) external  => DISPATCHER(true);
    function _.transfer(address,uint256) external  => DISPATCHER(true);
    function _.transferFrom(address,address,uint256) external => DISPATCHER(true);
}

definition MAX_UINT256() returns mathint = 115792089237316195423570985008687907853269984665640564039457584007913129639935;


////////////////////////////////////////////////////////////////////////////////
////           #  shares and assets conversions                  /////
////////////////////////////////////////////////////////////////////////////////
rule conversionOfZero {
    uint256 convertZeroShares = erc4626Mock.convertToAssets(0);
    uint256 convertZeroAssets = erc4626Mock.convertToShares(0);

    assert convertZeroShares == 0,
        "converting zero shares must return zero assets";
    assert convertZeroAssets == 0,
        "converting zero assets must return zero shares";
}


////////////////////////////////////////////////////////////////////////////////
////           #  functions do not revert                 /////
////////////////////////////////////////////////////////////////////////////////
rule depositDoesNotRevert(uint256 assets, address receiver) {
    env e; 
    require e.msg.sender != 0;
    require e.msg.value == 0; 
    require e.msg.sender != currentContract; 
    require assets > 0 && assets < MAX_UINT256();
    require erc4626Mock.previewDeposit(assets) < MAX_UINT256();
    require (erc4626Mock.previewDeposit(assets) + erc4626Mock.balanceOf(receiver)) < MAX_UINT256();
    require receiver == e.msg.sender;

    require erc4626Mock.asset() == erc20Mock;

    require erc20Mock.balanceOf(e.msg.sender) == assets;
    require erc20Mock.allowance(e.msg.sender, erc4626Mock) == assets;

    mathint expectedShares = erc4626Mock.previewDeposit(assets);
    require (expectedShares + erc4626Mock.totalSupply()) < MAX_UINT256(); 
    erc4626Mock.deposit@withrevert(e, assets, receiver); 
    assert !lastReverted; 
}


////////////////////////////////////////////////////////////////////////////////
////           #  functions change state correctly                 /////
////////////////////////////////////////////////////////////////////////////////
rule depositChangesStateCorrectly(uint256 assets, address receiver) {
    env e; 
    require e.msg.sender != 0; 
    require e.msg.value == 0;
    require e.msg.sender != currentContract;
    require assets > 0 && assets < MAX_UINT256();
    require erc4626Mock.previewDeposit(assets) < MAX_UINT256();
    require (erc4626Mock.previewDeposit(assets) + erc4626Mock.balanceOf(receiver)) < MAX_UINT256();
    require receiver == e.msg.sender; 

    require erc4626Mock.asset() == erc20Mock;

    require erc20Mock.balanceOf(e.msg.sender) == assets;
    require erc20Mock.allowance(e.msg.sender, erc4626Mock) == assets;
    
    mathint senderSharesBalanceBefore = erc4626Mock.balanceOf(e.msg.sender);

    //mathint expectedShares = erc4626Mock.previewDeposit(assets);
    erc4626Mock.deposit(e, assets, receiver); 

    mathint senderSharesBalanceAfter = erc4626Mock.balanceOf(e.msg.sender);

    assert senderSharesBalanceAfter >= senderSharesBalanceBefore,
        "after deposit, sender's shares balance must increase";

}
