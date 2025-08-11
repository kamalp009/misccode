.tooltip-container {
  position: relative;
  display: inline-block;
}

.tooltip-trigger {
  cursor: pointer;
}

.tooltip-content {
  position: absolute;
  z-index: 1000;
  padding: 12px 16px;
  background-color: #333;
  color: white;
  border-radius: 6px;
  font-size: 14px;
  line-height: 1.4;
  max-width: 300px;
  word-wrap: break-word;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  opacity: 0;
  animation: fadeIn 0.3s ease-in-out forwards;
}

.tooltip-content::after {
  content: '';
  position: absolute;
  width: 0;
  height: 0;
  border: 6px solid transparent;
}

.tooltip-top {
  bottom: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
}

.tooltip-top::after {
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border-top-color: #333;
}

.tooltip-bottom {
  top: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
}

.tooltip-bottom::after {
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  border-bottom-color: #333;
}

.tooltip-left {
  right: calc(100% + 8px);
  top: 50%;
  transform: translateY(-50%);
}

.tooltip-left::after {
  left: 100%;
  top: 50%;
  transform: translateY(-50%);
  border-left-color: #333;
}

.tooltip-right {
  left: calc(100% + 8px);
  top: 50%;
  transform: translateY(-50%);
}

.tooltip-right::after {
  right: 100%;
  top: 50%;
  transform: translateY(-50%);
  border-right-color: #333;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

@media (max-width: 768px) {
  .tooltip-content {
    max-width: 250px;
    font-size: 13px;
  }
}
