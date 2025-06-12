import logging

def setup_logger(name, file_log_level=logging.INFO, console_log_level=logging.WARNING):
    """
    Set up a logger with the specified name and logging level.
    
    Args:
        name (str): The name of the logger.
        level (int): The logging level (default is logging.INFO).
    
    Returns:
        logging.Logger: Configured logger instance.
    """

    log_entry_format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    
    # Setup logging
    logging.basicConfig(filename=f"{name}.log", format=log_entry_format)
    logger = logging.getLogger(name)
    logger.setLevel(file_log_level)

    # Create console handler
    ch = logging.StreamHandler()
    ch.setLevel(console_log_level)
    formatter = logging.Formatter(log_entry_format)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    logger.debug(f"logger setup with name: {name} and level: {logging.getLevelName(file_log_level)}")
    
    return logger